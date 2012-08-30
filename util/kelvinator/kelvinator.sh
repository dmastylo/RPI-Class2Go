#!/bin/bash
#
# Drive the frame extraction and differencing steps
# 
# This basically has two modes.  If the file given is right in the directory where
# frameExtractor and extractFrames.py are, then it will run locally and put the 
# results in the jpegs directory.
#
# The more common mode is for the source to be given as a URL to S3, like this:
#    frameExtractor s3://prod-c2g/nlp/Fall2012/Videos/11/RegularExpression.m4v 1 15
# in this case the script will use the s3cmd utilities to download the video, do the
# work locally, and then upload the result back to S3.
# 
# Assumes this is being run from the directory right above the kelvinator directory.
#
# This is pretty fragile as written now, needs a lot of error handling and hardning.

set -e     # fail on errors

if [[ $# -ne 3 ]]; then
    echo "usage: frameExtract <video> <rate> <thresh>"
    echo "   video    video name, assumed to be in current directory unless fully qualified path"
    echo "   rate     frames per second to extract (1 is good)"
    echo "   thresh   difference threshold to keep different frams (15 is good)"
    exit 1
fi

me=`basename $0`

echo
echo
echo -ne "$me: BEGINNING RUN at "
echo `date`
echo "$me: PROCESSING: $1"
echo

# we assume that working_path is writeable
working_path="/opt/class2go/kelvinator"
today_epoch=`date +%s`
working_dir="${working_path}/extract-${today_epoch}"
mydir=`pwd`

source_dir="."
using_s3=0
# if first character is a slash, then full path, extract it
# otherwise assume it's right here.  
if [[ ${1:0:5} == "s3://" || ${1:0:5} == "S3://" ]]; then
    source_dir=`dirname $1`
    using_s3=1
fi
video_file=`basename $1`

if [[ $using_s3 == 1 ]]; then
    echo "$me: setting up working directory: ${working_dir}"
    mkdir -p ${working_dir} 
    s3cmd -v get $1 ${working_dir}/$video_file

    pushd ${working_dir}   # yes, this is fragile
fi

frame_dir=jpegs

if [[ ! -d ${frame_dir} ]]; then
    echo "$me: creating target directory: ${frame_dir}"
    mkdir -p ${frame_dir} 
fi

if [[ -e ${frame_dir}/* ]]; then
    echo "$me: files already in target, clearing out: ${frame_dir}"
    rm -v ${frame_dir}/*
fi

#Runs ffmpeg to extract frames at a certain interval
echo
echo "$me: Starting Extraction (ffmpeg)"
# ffmpeg -i $video_file -r $2 -f image2 -s vga jpegs/img%3d.jpeg 
ffmpeg -i $video_file -r $2 -f image2 jpegs/img%3d.jpeg 

#Runs extractFrames to list frames to be deleted
echo
echo "$me: Starting Differencing (extractFrames.py)"
python $mydir/differenceFrames.py $3 $2

#Deletes all images listed in file toDelete
myFile="toDelete.txt"
myLine=""
while [ 1 ]
do
    read myLine || break
    rm ${frame_dir}/$myLine 
done < $myFile

# if we are doing in place then we are done.  But if we are using S3 we need to 
# upload files (and manifest) back up there

if [[ $using_s3 == 1 ]]; then
    echo "$me: copying frames to target: $source_dir/$frame_dir"
    s3cmd -v put --recursive $frame_dir ${source_dir}/

    popd
    echo "$me: cleaning up working directory: $working_dir"
    rm -rv $working_dir
fi

echo
echo -ne "$me: ENDING RUN at "
echo `date`
