# Kelvinator
#
# Simple method of extracting key frames for a video.  
#
# Requirements
# 1. ffmpeg (and in system path)
# 2. Pything Imaging: PIL, or Image
#

import sys
import os
import shutil
import imp
from django.core.files.storage import default_storage
from django.conf import settings
import urllib, urllib2, urlparse
import subprocess
import math
import operator
import Image
import logging
import time
import tempfile
from celery import task

logger = logging.getLogger(__name__)
    
# from http://mail.python.org/pipermail/image-sig/1997-March/000223.html
def computeDiff(file1, file2):
    h1 = Image.open(file1).histogram()
    h2 = Image.open(file2).histogram()
    rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
    return rms
    
def dir_create(path):
    if not os.path.isdir(path):
        os.mkdir(path)
        if not os.path.isdir(path):
            raise KelvinatorError("Unable to create dir: " % path)

def dir_remove(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
        if os.path.isdir(path):
            raise KelvinatorError("Unable to remove dir (recursively): " % path)

class KelvinatorError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

@task()
def kelvinate(s3_path_raw, input_frames_per_min='0'):
    """
    Given a path to a video in a readable S3 bucket, extract the frames and 
    upload back to S3.

    s3_path must be the path to the video file, not just to its parent folder
    """
    
    extractionFrameRate = 1   # seconds
    startOffset = 3           # seconds
    
    input_frames_per_min = float(input_frames_per_min)

    # normalizes url by lowercasing path, dropping query parameters and fragments
    o=urlparse.urlsplit(s3_path_raw)
    s3_path=o.geturl()
    
    # Verify that all working folders on local storage are creatable _and_ created,
    # that the video is the draft instance, and that the current video is not 
    # already kelvinating
    s3_path_parts = s3_path.split('/')
    video_filename = s3_path_parts[-1]
    video_id = s3_path_parts[-2]
    course_suffix = s3_path_parts[-4]
    course_prefix = s3_path_parts[-5]
    
    # Create working dir.  If this fails, we log something but otherwise let the 
    # exception go since we want it to fail violently which will leave the job
    # on the work queue.
    working_dir_parent = getattr(settings, "KELVINATOR_WORKING_DIR", "/tmp")
    try:
        working_dir=tempfile.mkdtemp(prefix="kelvinator-", dir=working_dir_parent)
    except:
        logger.error("Kelvinator error when creating temp file in \"%s\"" % working_dir_parent)
        raise
    logger.info("Working directory: " + working_dir)

    jpeg_dir = working_dir + "/jpegs"
    dir_create(jpeg_dir)
    
    logger.info("Reading from S3: " + s3_path)
    dl_handle = urllib2.urlopen(s3_path)

    video_file = working_dir + "/" + video_filename
    logger.info("Writing to working (local) file: " + video_file)
    videoFile = open(video_file, 'wb')
    videoFile.write(dl_handle.read())
    videoFile.close()
    
    # TODO: consider some retry logic here
    try:
        filesize = os.path.getsize(video_file)
    except os.error as e:
        logger.error("Unable to download video file from S3")
        raise e

    if filesize == 0:
        raise KelvinatorError("file size zero, video file did not download properly")
    
    logger.info("Kicking off ffmpeg, hold onto your hats")
    returncode = subprocess.call(['ffmpeg', 
        '-i', video_file,                   # input
        '-ss', str(startOffset),            # start a few seconds late
        '-r', str(extractionFrameRate),     # thumbs per second to extract
        '-f', 'image2',                     # thumb format
        jpeg_dir + '/img%5d.jpeg',          # thumb filename template
        ])

    logger.info("ffmpeg completed, returncode %d" % returncode)
    if returncode != 0:
        raise KelvinatorError
    
    image_list = os.listdir(jpeg_dir)
    if len(image_list) == 0:
        raise KelvinatorError("Failed to extract keyframes from video file")
        
    image_list.sort()
    logger.info("Extraction frame rate: %d fps" % extractionFrameRate)
    duration = len(image_list)/extractionFrameRate    # in seconds
    logger.info("Video duration: %d seconds" % duration)
    logger.info("Initial keyframes: %d" % len(image_list))
    if input_frames_per_min <= 0:
        logger.info("Target keyframes per minute = 2 (default)")
        input_frames_per_min = 2
    else:
        logger.info("Target keyframes per minute = %d" % input_frames_per_min)
    
    max_keyframes = int(math.ceil(input_frames_per_min * duration/60.0))
    logger.info("Upper bound on number of keyframes kelvinator will output: %d" % max_keyframes)
    logger.info("Internal differencing threshold: 1000")

    differences = [1000000000]
    differences_sorted = [1000000000]
    for i in range(len(image_list)-1):
        diff = computeDiff(jpeg_dir+'/'+image_list[i], jpeg_dir+'/'+image_list[i+1])
        differences.append(diff)
        differences_sorted.append(diff)
    
    differences_sorted.sort(reverse=True)
    if len(differences_sorted) <= max_keyframes:
        # The number of extracted keyframes is lte to the max allowable 
        # keyframe count. Keep all
        threshold = differences_sorted[len(differences_sorted)-1] 
        term_reason = "Number of initial frames was lte to the maximum number of keyframes allowed"
    elif differences_sorted[max_keyframes-1] > 1000: 
        # Too many keyframes will be generated. Choose higher threshold to 
        # force the number of keyframes down to max_keyframes.
        threshold = differences_sorted[max_keyframes-1]
        term_reason = "Capped by maximum number of keyframes allowed"
    else:
        threshold = 1000
        term_reason = "Capped by internal threshold"
    
    keepList = []
    keepIndicies = []
    deleteList = []
    
    for i in range(len(image_list)-1):
        if differences[i] >= threshold:
            keepList.append(image_list[i])
            keepIndicies.append(i)
        else:
            os.remove(jpeg_dir+'/'+image_list[i])

    logger.info("Keyframes selected: %d" % len(keepList))
    logger.info("Termination reason: %s" % term_reason)
    
    os.remove(jpeg_dir+'/'+image_list[len(image_list)-1])
    
    # Write out manifest
    outfile = jpeg_dir + "/manifest.txt"
    FILE = open(outfile, "w")
    index = 0
    FILE.write("{")

    while(index < len(keepList)):
        FILE.write("\"")
        toWrite = str(keepIndicies[index])
        FILE.write(toWrite)
        FILE.write("\":{\"imgsrc\":\"")
        FILE.write(keepList[index])
        FILE.write("\"}")
        if index < len(keepList)-1:
            FILE.write(",")
        index += 1
    FILE.write("}")
    FILE.close()
    
    # Upload manifest and jpegs to S3
    
    image_list = os.listdir(jpeg_dir)
    image_list.sort()
    
    for file in image_list:
        local_file = open(jpeg_dir + '/' + file, 'rb')
        s3_file = default_storage.open(course_prefix + '/' + course_suffix + '/videos/' + str(video_id) + '/jpegs/' + file, 'wb')
        file_data = local_file.read();
        s3_file.write(file_data)
        local_file.close()
        s3_file.close()
    
    # Cleanup

    logger.info("Cleaning up working dir: " + working_dir)
    dir_remove(working_dir)

    return

