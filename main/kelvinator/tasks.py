# Video handling utilities.
#
# Two things in this file
# 1. Kelvinator - simple method of extracting key frames for a video.  
# 2. Resize - simple transcoder to create smaller versions of videos.
#
# Requirements:
# 1. ffmpeg 
# 2. x264 for transcoding
# 3. Python Imaging: PIL, or Image
#
# For more info on transcoding, see: 
# - http://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide
# size abbreviations: 
# - http://linuxers.org/tutorial/how-extract-images-video-using-ffmpeg

import sys
import os
import subprocess
import math
import operator
import time
import numpy as np
import shutil

from django.core.files.storage import default_storage
from django.conf import settings
from celery import task

import Image

from utility import *

##
##  KELVINATOR
##

def extract(notify_buf, working_dir, jpeg_dir, video_file, start_offset, extraction_frame_rate):
    infoLog(notify_buf, "Kicking off ffmpeg, hold onto your hats")
    cmdline = [ ffmpeg_cmd() ]
    cmdline += \
        [ '-i', working_dir + "/" + video_file, # input
          '-ss', str(start_offset),             # start a few seconds late
          '-r', str(extraction_frame_rate),     # thumbs per second to extract
          '-f', 'image2',                       # thumb format
          jpeg_dir + '/img%5d.jpeg',            # thumb filename template
        ]
    infoLog(notify_buf, "EXTRACT: " + " ".join(cmdline))
    returncode = subprocess.call(cmdline)

    if returncode == 0:
        infoLog(notify_buf, "ffmpeg completed, returncode %d" % returncode)
    else:
        errorLog(notify_buf, "ffmpeg completed, returncode %d" % returncode)
        cleanup_working_dir(notify_buf, working_dir)
        raise VideoError("ffmpeg error %d" % returncode)


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

    # get local maximum values from an array, which are also larger the threshold. 
    # local maximum is extracted by comparing current with three neighbors in both directions. 
    def localMaximum(candidates, threshold):
        cuts = [];
        for i in range(3, len(candidates)-4):
            cur_score = candidates[i][0]
            if cur_score > threshold and cur_score > candidates[i-1][0] and cur_score > candidates[i-2][0] and cur_score > candidates[i-3][0] and cur_score > candidates[i+1][0] and cur_score > candidates[i+2][0] and cur_score > candidates[i+3][0] :
                cuts.append(candidates[i])
        return cuts

    image_list = os.listdir(jpeg_dir)
    if len(image_list) == 0:
        cleanup_working_dir(notify_buf, working_dir)
        raise VideoError("Failed to extract keyframes from video file")
        
    image_list.sort()
    infoLog(notify_buf, "Extraction frame rate: %d fps" % extraction_frame_rate)
    duration = len(image_list)/extraction_frame_rate    # in seconds
    infoLog(notify_buf, "Video duration: %d seconds" % duration)
    infoLog(notify_buf, "Initial keyframes: %d" % len(image_list))
    infoLog(notify_buf, "Target keyframes per minute: %d" % frames_per_minute_target) 
    max_keyframes = int(math.ceil(frames_per_minute_target * duration/60.0))
    infoLog(notify_buf, "Upper bound on number of keyframes kelvinator will output: %d" % max_keyframes)
    infoLog(notify_buf, "Internal differencing threshold: average of all scores")
    image_num = len(image_list)

    # window size, all the frames in the window centered at 
    # current frame are used to determine shot boundary. 
    # this value doesn't need to be changed for different videos.
    k = 5

    # calculate difference matrix
    difference_matrix = np.zeros((image_num,image_num))
    for i in range(0, image_num-1-k):
        for j in range(i+1, i+k):
            difference_matrix[i, j] = computeDiff(jpeg_dir+"/"+image_list[i], jpeg_dir+"/"+image_list[j])
    difference_matrix = difference_matrix + difference_matrix.transpose()
    
    # callate shot boundary scores for each frames, score = cut(A,B)/associate(A) + cut(A,B)/associate(B) 
    candidates = []
    for i in range(k, image_num-1-k):
        cutAB = np.sum(difference_matrix[i-k:i, i:i+k])
        assocA = np.sum(difference_matrix[i-k:i, i-k:i])
        assocB = np.sum(difference_matrix[i:i+k, i:i+k])
        if (assocA!=0) and (assocB!=0):
            score = cutAB/assocA + cutAB/assocB
        else:
            score = 0
        candidates.append((score, i))

    # extract local maximum as the shot boundaries.
    # the threshold is assigned to be the mean of all the scores. 
    # [important] we may want to change the threshold to control the number of key frames. 
    # higher threshold generates fewer shot boundaries.
    threshold = np.mean([pair[0] for pair in candidates]);
    cuts = localMaximum(candidates, threshold)

    # limit shot boundary number fewer than max_keyframes
    if len(cuts) >= max_keyframes :
        # sort key frames by score 
        cuts.sort(reverse=True)
        cuts = cuts[:max_keyframes];

    # select the 3nd frame after each shot boundary as the key frame.
    # alternatively, we can also select middle frame between two shot boundaries as the key frame.
    cut_offset = 2

    # below code is used to output keyframes.
    keep_frames = []
    keep_times = []
    jpeg_dir_parent = os.path.abspath(os.path.join(jpeg_dir, os.path.pardir))
    jpeg_dir_result = jpeg_dir_parent + "/tmp"
    if os.path.exists(jpeg_dir_result):
        pass
    else:
        os.mkdir(jpeg_dir_result)
    # sort key frames by index
    sorted(cuts, key=lambda x: x[1])     

    # move key frames into a tmp folder, then move back.
    for i in range(len(cuts)):
        index = min(cuts[i][1] + cut_offset, len(image_list) - 1)
        shutil.move(jpeg_dir+"/"+image_list[index], jpeg_dir_result)
        keep_frames.append(image_list[index])
        keep_times.append(index)

    cleanup_working_dir(notify_buf, jpeg_dir)
    os.rename(jpeg_dir_result, jpeg_dir)  

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


def put_thumbs(notify_buf, jpeg_dir, prefix, suffix, video_id, store_loc):
    # I wish Filesystem API worked the same for local and remote, but it don't
    if store_loc == 'local':
        root = getattr(settings, 'MEDIA_ROOT')
        store_path = root + "/" + prefix + "/" + suffix + "/videos/" + str(video_id) + "/jpegs"
        if default_storage.exists(store_path):
            infoLog(notify_buf, "Found prior directory, removing: %s" % store_path)
            dirRemove(store_path) 
        os.mkdir(store_path)
    else:
        store_path = prefix + "/" + suffix + "/videos/" + str(video_id) + "/jpegs"
        default_storage.delete(store_path)

    # not doing write to tmp and then mv because the file storage API limitation
    image_list = os.listdir(jpeg_dir)
    image_list.sort()
    for fname in image_list:
        infoLog(notify_buf, "Uploading: %s" % fname)
        local_file = open(jpeg_dir + "/" + fname, 'rb')
        store_file = default_storage.open(store_path + "/" + fname, 'wb')
        file_data = local_file.read()
        store_file.write(file_data)
        local_file.close()
        store_file.close()
    infoLog(notify_buf, "Uploaded: %s files" % str(len(image_list)))


# Main Kelvinator Task (CELERY)

@task()
def kelvinate(store_path_raw, frames_per_minute_target=2, notify_addr=None):
    """
    Given a path to a video in a readable S3 bucket, extract the frames and 
    upload back to S3.

    store_path must be the full path to the video file, not just to its parent folder.
    """

    notify_buf = []

    infoLog(notify_buf, "Kelvinate: extracting %s" % store_path_raw)

    extraction_frame_rate = 1   # seconds
    start_offset = 3            # seconds
    
    frames_per_minute_target = float(frames_per_minute_target)

    (store_path, course_prefix, course_suffix, video_id, video_filename) = splitpath(store_path_raw)

    store_loc = "remote"
    if getattr(settings, 'AWS_ACCESS_KEY_ID') == "local":
        store_loc = "local"

    work_dir = None
    try:
        (work_dir, jpegs) = create_working_dirs("kelvinator", notify_buf, "jpegs")
        get_video(notify_buf, work_dir, video_filename, store_path)
        extract(notify_buf, work_dir, jpegs, video_filename, start_offset, extraction_frame_rate)
        (thumbs, times) = difference(notify_buf, work_dir, jpegs, extraction_frame_rate, frames_per_minute_target)
        write_manifest(notify_buf, jpegs, thumbs, times)
        put_thumbs(notify_buf, jpegs, course_prefix, course_suffix, video_id, store_loc)
    except:
        if work_dir: cleanup_working_dir(notify_buf, work_dir)
        notify("Kelvinator", notify_buf, notify_addr, 
                course_prefix, course_suffix, video_filename, store_path) # in utilities.py
        raise

    cleanup_working_dir(notify_buf, work_dir)
    notify("Kelvinator", notify_buf, notify_addr, course_prefix, course_suffix, video_filename, store_path)




##
##  RESIZE
##

# video sizes we support: key is size name (used for target subdirectory) and value
# are the parameters (as a list) that we'll pass to ffmpeg.
sizes = { "large":  [ "-crf", "23", "-s", "1280x720" ],   # original size, compressed
          "medium": [ "-crf", "27", "-s", "852x480" ],    # wvga at 16:9
          "small":  [ "-crf", "30", "-s", "640x360" ],    
          "tiny":   [ "-crf", "40", "-s", "320x180" ],
        }


# Actually transcode the video down 
def do_resize(notify_buf, working_dir, target_dir, video_file, target_size):
    cmdline = [ ffmpeg_cmd() ]
    cmdline += [ "-i", working_dir + "/" + video_file,  # infile
                 "-c:v", "libx264",          # video codec
                 "-profile:v", "baseline",   # most compatible
                 "-strict", "-2",            # magic to allow aac audio enc
               ]
    cmdline += sizes[target_size]
    cmdline += [ target_dir + "/" + video_file ]  # outfile

    infoLog(notify_buf, "RESIZE: " + " ".join(cmdline))
    returncode = subprocess.call(cmdline)

    if returncode == 0:
        infoLog(notify_buf, "completed with returncode %d" % returncode)
    else:
        errorLog(notify_buf, "completed with returncode %d" % returncode)
        cleanup_working_dir(notify_buf, working_dir)
        raise VideoError("do_resize error %d" % returncode)


def upload(notify_buf, target_dir, target_part, prefix, suffix, video_id, video_file, store_loc):
    # I wish Filesystem API worked the same for local and remote, but it don't
    if store_loc == 'local':
        root = getattr(settings, 'MEDIA_ROOT')
        store_path = root + "/" + prefix + "/" + suffix + "/videos/" + str(video_id) + "/" + target_part
        if default_storage.exists(store_path):
            infoLog(notify_buf, "Found prior directory, removing: %s" % store_path)
            dirRemove(store_path) 
        os.mkdir(store_path)
    else:
        store_path = prefix + "/" + suffix + "/videos/" + str(video_id) + "/" + target_part
        default_storage.delete(store_path)

    statinfo = os.stat(target_dir + "/" + video_file)
    infoLog(notify_buf, "Final file size: %s" % str(statinfo.st_size))

    local_file = open(target_dir + "/" + video_file, 'rb')
    store_file = default_storage.open(store_path + "/" + video_file, 'wb')
    store_file.write(local_file.read())
    local_file.close()
    store_file.close()


# Main Resize Task (CELERY)

@task()
def resize(store_path_raw, target_raw, notify_addr=None):
    """
    Given a video path, scale it down and save the result alongside the original
    video.  So we can provide different download options.

    Preset is either "small" or "large".
    """

    notify_buf = []
    infoLog(notify_buf, "Resize: converting %s version of %s" % (target_raw, store_path_raw))

    target = target_raw.lower()
    if target not in sizes.keys():
        VideoError("Target size \"%s\" not supported" % target)

    (store_path, course_prefix, course_suffix, video_id, video_file) = splitpath(store_path_raw)

    store_loc = 'remote'
    if getattr(settings, 'AWS_ACCESS_KEY_ID') == 'local':
        store_loc = 'local'

    work_dir = None
    try:
        (work_dir, smaller_dir) = create_working_dirs("resize", notify_buf, target)
        get_video(notify_buf, work_dir, video_file, store_path)
        do_resize(notify_buf, work_dir, smaller_dir, video_file, target)
        upload(notify_buf, smaller_dir, target, course_prefix, course_suffix, video_id, video_file, store_loc)
    except:
        if work_dir: cleanup_working_dir(notify_buf, work_dir)
        notify("Resize (%s)" % target, notify_buf, notify_addr, course_prefix, course_suffix, 
               video_file, store_path)
        raise

    cleanup_working_dir(notify_buf, work_dir)
    notify("Resize (%s)" % target, notify_buf, notify_addr, course_prefix, course_suffix, 
           video_file, store_path)

