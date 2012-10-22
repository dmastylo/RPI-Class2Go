#= Kelvinator
#
# Simple method of extracting key frames for a video.  
#
# Requirements
# 1. ffmpeg (and in system path)
# 2. Pything Imaging: PIL, or Image
#

import sys
import os, socket
import shutil
import imp
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.mail import send_mail
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
    

##
## HELPER FUNCTIONS
##

# relying on buf being a list (mutable) so it is passed by reference

def infoLog(buf, l):
    buf.append(l)
    logger.info(l)

def errorLog(buf, l):
    buf.append("ERROR: %s" % l)
    logger.error(l)


def dirRemove(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
        if os.path.isdir(path):
            raise KelvinatorError("Unable to remove dir: %s" % path)

class KelvinatorError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

##
## MAIN FUNCTIONS
##

def create_working_dir(notify_buf):
    """
    Create local temp director where we will do our work.  If this fails, we log 
    something but otherwise let the exception go since we want it to fail violently 
    which will leave the job on the work queue.
    """

    working_dir_parent = getattr(settings, "KELVINATOR_WORKING_DIR", "/tmp")
    try:
        working_dir=tempfile.mkdtemp(prefix="kelvinator-", dir=working_dir_parent,
                suffix="-" + str(os.getpid()))
    except:
        errorLog(notify_buf, "Kelvinator error when creating temp file in \"%s\"" % working_dir_parent)
        raise
    infoLog(notify_buf, "Working directory: " + working_dir)

    jpeg_dir = working_dir + "/jpegs"
    try:
        os.mkdir(jpeg_dir)
    except OSError:
        raise KelvinatorError("cannot create \"%s\", potential collision" % jpeg_dir)
    if not os.path.isdir(jpeg_dir):
        raise KelvinatorError("Unable to create dir: " + jpeg_dir)

    return (working_dir, jpeg_dir)


def get_video(notify_buf, working_dir, video_filename, source_path):
    infoLog(notify_buf, "Source file: " + source_path)
    source_file = default_storage.open(source_path)

    video_file = working_dir + "/" + video_filename
    infoLog(notify_buf, "Writing to working (local) file: " + video_file)
    working_file = open(video_file, 'wb')
    working_file.write(source_file.read())
    working_file.close()
    source_file.close()
    
    # TODO: consider some retry logic here
    try:
        filesize = os.path.getsize(video_file)
    except os.error:
        errorLog(notify_buf, "Unable to download video file")
        cleanup_working_dir(notify_buf, working_dir)
        raise 

    if filesize == 0:
        cleanup_working_dir(notify_buf, working_dir)
        raise KelvinatorError("file size zero, video file did not download properly")


def extract(notify_buf, working_dir, jpeg_dir, video_file, start_offset, extraction_frame_rate):
    infoLog(notify_buf, "Kicking off ffmpeg, hold onto your hats")
    returncode = subprocess.call(['ffmpeg', 
        '-i', working_dir + "/" + video_file,  # input
        '-ss', str(start_offset),              # start a few seconds late
        '-r', str(extraction_frame_rate),      # thumbs per second to extract
        '-f', 'image2',                        # thumb format
        jpeg_dir + '/img%5d.jpeg',             # thumb filename template
        ])

    if returncode == 0:
        infoLog(notify_buf, "ffmpeg completed, returncode %d" % returncode)
    else:
        errorLog(notify_buf, "ffmpeg completed, returncode %d" % returncode)
        cleanup_working_dir(notify_buf, working_dir)
        raise KelvinatorError("ffmpeg error %d" % returncode)


def difference(notify_buf, working_dir, jpeg_dir, extraction_frame_rate, frames_per_minute_target):
    """
    Sherif's method for figuring out what frames to keep from the candidate
    set to reach the targeted number of slides.
    """

    # from http://mail.python.org/pipermail/image-sig/1997-March/000223.html
    def computeDiff(file1, file2):
        h1 = Image.open(file1).histogram()
        h2 = Image.open(file2).histogram()
        rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
        return rms
    
    image_list = os.listdir(jpeg_dir)
    if len(image_list) == 0:
        cleanup_working_dir(notify_buf, working_dir)
        raise KelvinatorError("Failed to extract keyframes from video file")
        
    image_list.sort()
    infoLog(notify_buf, "Extraction frame rate: %d fps" % extraction_frame_rate)
    duration = len(image_list)/extraction_frame_rate    # in seconds
    infoLog(notify_buf, "Video duration: %d seconds" % duration)
    infoLog(notify_buf, "Initial keyframes: %d" % len(image_list))
    infoLog(notify_buf, "Target keyframes per minute: %d" % frames_per_minute_target)
    
    max_keyframes = int(math.ceil(frames_per_minute_target * duration/60.0))
    infoLog(notify_buf, "Upper bound on number of keyframes kelvinator will output: %d" % max_keyframes)
    infoLog(notify_buf, "Internal differencing threshold: 1000")

    differences = [1000000000]
    differences_sorted = [1000000000]
    for i in range(len(image_list)-1):
        diff = computeDiff(jpeg_dir+"/"+image_list[i], jpeg_dir+"/"+image_list[i+1])
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
    
    keep_frames = []
    keep_times = []
    
    for i in range(len(image_list)-1):
        if differences[i] >= threshold:
            keep_frames.append(image_list[i])
            keep_times.append(i)
        else:
            os.remove(jpeg_dir+"/"+image_list[i])

    infoLog(notify_buf, "Keyframes selected: %d" % len(keep_frames))
    infoLog(notify_buf, "Termination reason: %s" % term_reason)
    
    os.remove(jpeg_dir+"/"+image_list[len(image_list)-1])

    return (keep_frames, keep_times)


def write_manifest(notify_buf, jpeg_dir, keep_frames, keep_times):
    outfile_name = jpeg_dir + "/manifest.txt"
    outfile = open(outfile_name, 'w')
    index = 0
    outfile.write("{")

    while(index < len(keep_frames)):
        outfile.write("\"")
        toWrite = str(keep_times[index])
        outfile.write(toWrite)
        outfile.write("\":{\"imgsrc\":\"")
        outfile.write(keep_frames[index])
        outfile.write("\"}")
        if index < len(keep_frames)-1:
            outfile.write(",")
        index += 1
    outfile.write("}")
    outfile.close()


def put_thumbs(notify_buf, jpeg_dir, prefix, suffix, video_id, store_path, store_loc):
    # I wish Filesystem API worked the same for local and remote, but it don't
    if store_loc == 'local':
        root = getattr(settings, 'MEDIA_ROOT')
        store_path = root + "/" + prefix + "/" + suffix + "/videos/" + str(video_id) + "/jpegs"
        if default_storage.exists(store_path):
                dirRemove(store_path) 
        os.mkdir(store_path)
    else:
        store_path = prefix + "/" + suffix + "/videos/" + str(video_id) + "/jpegs"
        default_storage.delete(store_path)

    # not doing write to tmp and then mv because the file storage API limitation
    image_list = os.listdir(jpeg_dir)
    image_list.sort()
    for fname in image_list:
        local_file = open(jpeg_dir + "/" + fname, 'rb')
        store_file = default_storage.open(store_path + "/" + fname, 'wb')
        file_data = local_file.read();
        store_file.write(file_data)
        local_file.close()
        store_file.close()


def cleanup_working_dir(notify_buf, working_dir):
    infoLog(notify_buf, "Cleaning up working dir: " + working_dir)
    dirRemove(working_dir)


def notify(notify_buf, notify_addr, prefix, suffix, filename, store_path):
    if notify_addr is None: return

    subject = "Kelvinator result: %s %s %s" % (prefix, suffix, filename)

    body =  "course: %s %s\n" % (prefix, suffix)
    body += "video file: %s\n" % store_path
    body += "machine: %s\n" % socket.gethostname()
    body += "\n"
    body += "-------- LOG --------\n"
    body += "\n"
    body += "\n".join(notify_buf)

    send_mail(subject, body, "noreply@class.stanford.edu", [ notify_addr, ])



##
## CELERY TASK
##

@task()
def kelvinate(store_path_raw, frames_per_minute_target=2, notify_addr=None):
    """
    Given a path to a video in a readable S3 bucket, extract the frames and 
    upload back to S3.

    store_path must be the full path to the video file, not just to its parent folder.
    """

    notify_buf = []

    extraction_frame_rate = 1   # seconds
    start_offset = 3            # seconds
    
    frames_per_minute_target = float(frames_per_minute_target)

    # normalizes url by lowercasing path, dropping query parameters and fragments
    store_path = urlparse.urlsplit(store_path_raw).geturl()
    
    store_path_parts = store_path.split("/")
    course_prefix = store_path_parts[-5]
    course_suffix = store_path_parts[-4]
    video_id = store_path_parts[-2]
    video_filename = store_path_parts[-1]

    storage = "remote"
    if getattr(settings, 'AWS_ACCESS_KEY_ID') == "local":
        storage = "local"

    work_dir = None
    try:
        (work_dir, jpegs) = create_working_dir(notify_buf)
        get_video(notify_buf, work_dir, video_filename, store_path)
        extract(notify_buf, work_dir, jpegs, video_filename, start_offset, extraction_frame_rate)
        (thumbs, times) = difference(notify_buf, work_dir, jpegs, extraction_frame_rate, frames_per_minute_target)
        write_manifest(notify_buf, jpegs, thumbs, times)
        put_thumbs(notify_buf, jpegs, course_prefix, course_suffix, video_id, store_path, storage)
    except:
        if work_dir: cleanup_working_dir(notify_buf, work_dir)
        notify(notify_buf, notify_addr, course_prefix, course_suffix, video_filename, store_path)
        raise

    cleanup_working_dir(notify_buf, work_dir)
    notify(notify_buf, notify_addr, course_prefix, course_suffix, video_filename, store_path)

