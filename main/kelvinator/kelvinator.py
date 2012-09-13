import sys
import os
from os import path
import imp
from django.core.files.storage import default_storage
import urllib, urllib2
import subprocess
import math
import operator
import Image

### CAUTION: This file is sensivitve to the path main/database.py

# The Kelvinator requires the following:
# 1. ffmpeg to be installed and the system path to be configured so that you can invoke commands of the form ffmpeg ... from any directory from your prompt
# 2. PIL to be installed



def SanitizeS3Path(s3_path):
    qm = s3_path.find('?')
    if qm > 0:
        s3_path = s3_path[0:qm-1]
    return s3_path
    
# from http://mail.python.org/pipermail/image-sig/1997-March/000223.html
def computeDiff(file1, file2):
    h1 = Image.open(file1).histogram()
    h2 = Image.open(file2).histogram()
    rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
    return rms
    
def cleanUp(video_path):
    jpeg_path = video_path + '/jpegs'
    if os.path.exists(video_path):
        if os.path.exists(jpeg_path):
            file_list = os.listdir(jpeg_path)
            for file in file_list:
                if file != '.' and file != '..':
                    os.remove(jpeg_path + '/' + file)
            os.rmdir(jpeg_path)
        file_list = os.listdir(video_path)
        for file in file_list:
            if file != '.' and file != '..':
                os.remove(video_path + '/' + file)
        os.rmdir(video_path)
    
def isKelvinating(video):
    assert KELVINATOR_WORKING_PATH != '' and os.path.isdir(KELVINATOR_WORKING_PATH), "Error: KELVINATOR_WORKING_PATH was not configured properly in database.py!"
    if video.mode == 'ready':
        video = video.image # Many things are based on the draft video ID
    course = video.course
    course_handle = course.handle.replace('--','')
    return False
    return os.path.isdir(KELVINATOR_WORKING_PATH + course_handle + '/' + str(video.id))

def run_cmd():
    s3_path = sys.argv[1]
    
    arg_keyframes_per_minute = '0'
    if len(sys.argv) > 1:
        arg_keyframes_per_minute = sys.argv[2]
        
    return run(s3_path, arg_keyframes_per_minute)
    
   
def run(s3_path, arg_keyframes_per_minute='0'):
    import pdb; pdb.set_trace();
    d1 = __file__
    while d1[-4:] != "main":
        if len(d1) < 4:
            print "Error: Couldn't find database.py in folder 'main'!"
            return
        d1 = os.path.dirname(d1)
        
    database_py = imp.load_source('settings', d1+"/database.py")
    KELVINATOR_WORKING_PATH = database_py.KELVINATOR_WORKING_PATH
    
    # s3_path must be the path to the video file, not just to its parent folder
    
    info = []
    arg_keyframes_per_minute = float(arg_keyframes_per_minute)

    ### Sanity Checks  and Folder Creation ###
    
    s3_path = SanitizeS3Path(s3_path)
    
    ## Verify that all working folders on local storage are creatable _and_ created, that the video is the draft instance, and that the current video is not already kelvinating
    s3_path_parts = s3_path.split('/')
    video_filename = s3_path_parts[-1]
    video_id = s3_path_parts[-2]
    course_suffix = s3_path_parts[-4]
    course_prefix = s3_path_parts[-5]
    
    # Verify that KELVINATOR_WORKING_PATH is a valid path
    assert KELVINATOR_WORKING_PATH != '' and os.path.isdir(KELVINATOR_WORKING_PATH), "Error: KELVINATOR_WORKING_PATH was not configured properly in database.py!"
    
    # If course doesn't yet have a folder in KELVINATOR_WORKING_PATH, create one
    if not os.path.isdir(KELVINATOR_WORKING_PATH + '/' + course_prefix):
        os.mkdir(KELVINATOR_WORKING_PATH + '/' + course_prefix)
        assert os.path.isdir(KELVINATOR_WORKING_PATH + course_prefix), "Error: Unable to create course folder in KELVINATOR_WORKING_PATH!"
    if not os.path.isdir(KELVINATOR_WORKING_PATH + '/' + course_prefix + '/' + course_suffix):
        os.mkdir(KELVINATOR_WORKING_PATH + '/' + course_prefix + '/' + course_suffix)
        assert os.path.isdir(KELVINATOR_WORKING_PATH + course_prefix + '/' + course_suffix), "Error: Unable to create course folder in KELVINATOR_WORKING_PATH!"
    
    # Create Working Directory
    course_path = KELVINATOR_WORKING_PATH + course_prefix + '/' + course_suffix
    video_path = course_path + '/' + str(video_id)
    jpeg_path = video_path + '/jpegs'
    
    # Check if the video has kelvination assets. Delete them if so
    cleanUp(video_path)
        
    os.mkdir(video_path)
    assert os.path.isdir(video_path), "Error: Unable to create video kelvination folder. Permissions?"
    
    os.mkdir(jpeg_path)
    
    
    
    ### Attempt to download the video file from S3 ###
    video_file_path = video_path + '/' + video_filename
    dl_handle = urllib2.urlopen(s3_path)
    videoFile = open(video_file_path, 'wb')
    videoFile.write(dl_handle.read())
    videoFile.close()
    
    try:
        filesize = os.path.getsize(video_file_path)
        assert filesize > 0, "Error: Video file did not download properly"
    except:
        print "Unable to download video file from S3"
        return
    
    
    
    
    ### Running FFMPEG ###
    extractionFrameRate = 1
    subprocess.call(['ffmpeg', '-i', video_file_path, '-r', str(extractionFrameRate), '-f', 'image2', jpeg_path + '/img%5d.jpeg'])
    
    
    
    
    
    ### Selecting keyframes and deleting unneeded ones
    info.append({'Extraction frame rate': "%d fps" % extractionFrameRate})
    
    #Read in all the files names in jpegs folders as a list of strings
    imageList = os.listdir(jpeg_path)
    assert len(imageList) > 0, "Error: Failed to extract keyframes from video file!"
    imageList.sort()
    
    duration = len(imageList)/extractionFrameRate # in seconds
    info.append({'Video duration': "%d seconds" % duration})
    info.append({'Total number of initial keyframes': str(len(imageList))})
    if arg_keyframes_per_minute <= 0:
        info.append({'Desired number of keyframes per minute': "2 (no valid value passed in, default value of 2/min used)"})
        arg_keyframes_per_minute = 2
    else:
        info.append({'Desired number of keyframes per minute': "%d /min (value passed in by user)" % arg_keyframes_per_minute})
    
    max_keyframes = int(math.ceil(arg_keyframes_per_minute * duration/60.0))
    info.append({'Upper bound on number of keyframes kelvinator will output': str(max_keyframes)})
    
    info.append({'Internal differencing threshold': '1000'})
    
    differences = [1000000000]
    differences_sorted = [1000000000]
    for i in range(len(imageList)-1):
        diff = computeDiff(jpeg_path+'/'+imageList[i], jpeg_path+'/'+imageList[i+1])
        differences.append(diff)
        differences_sorted.append(diff)
    
    differences_sorted.sort(reverse=True)
    if len(differences_sorted) <= max_keyframes:
        threshold = differences_sorted[len(differences_sorted)-1] # The number of extracted keyframes is lte to the max allowable keyframe count. Keep all
        termination_reason = "Number of initial frames was lte to the maximum number of keyframes allowed"
    elif differences_sorted[max_keyframes-1] > 1000: # Too many keyframes will be generated. Choose higher threshold to force the number of keyframes down to max_keyframes.
        threshold = differences_sorted[max_keyframes-1]
        termination_reason = "Capped by maximum number of keyframes allowed"
    else:
        threshold = 1000
        termination_reason = "Capped by internal threshold"
    
    keepList = []
    keepIndicies = []
    deleteList = []
    
    for i in range(len(imageList)-1):
        if differences[i] >= threshold:
            keepList.append(imageList[i])
            keepIndicies.append(i)
        else:
            os.remove(jpeg_path+'/'+imageList[i])

    info.append({'Number of keyframes selected': str(len(keepList))})
    info.append({'Termination reason': termination_reason})
    
    os.remove(jpeg_path+'/'+imageList[len(imageList)-1])
    
    
    
    
    ### Writing out the manifest ###
    outfile = jpeg_path + "/manifest.txt"
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
    
    
    
    
    ### Upload the manifest and jpegs to S3 ###
    
    imageList = os.listdir(jpeg_path)
    imageList.sort()
    
    for file in imageList:
        local_file = open(jpeg_path + '/' + file, 'rb')
        s3_file = default_storage.open(course_prefix + '/' + course_suffix + '/videos/' + str(video_id) + '/jpegs/' + file, 'wb')
        file_data = local_file.read();
        s3_file.write(file_data)
        local_file.close()
        s3_file.close()
    
    
    
    ### Generate report ###
    report = ''
    for item in info:
        for key in item:
            report += "\t" + key + ":\t" + item[key] + "\n\n"
    
    ### Cleanup ###
    #cleanUp(video_path)
    
    return report
    
if __name__ == "__main__":
    run_cmd()
