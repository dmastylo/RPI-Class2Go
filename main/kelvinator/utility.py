import sys, os, socket, shutil
import tempfile
import logging
import urllib, urllib2, urlparse

from django.core.files.storage import default_storage
from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


def splitpath(raw):
    store_path = urlparse.urlsplit(raw).geturl()
    sp = store_path.split("/")
    course_prefix = sp[-5]
    course_suffix = sp[-4]
    video_id = sp[-2]
    video_filename = sp[-1]
    return (store_path, course_prefix, course_suffix, video_id, video_filename) 


def ffmpeg_cmd():
    if sys.platform == "darwin":
        cmd = "ffmpeg"
    elif sys.platform == "linux2":
        cmd = "/usr/local/bin/ffmpeg"   # hardcoded location since we need a special one
    else:
        VideoError("Platform not supported, got \"%s\" expected darwin or linux2" % sys.platform)
    return cmd


def create_working_dirs(job, notify_buf, subdir_name):
    """
    Create local temp director where we will do our work.  If this fails, we log 
    something but otherwise let the exception go since we want it to fail violently 
    which will leave the job on the work queue.
    """

    working_dir_parent = getattr(settings, "KELVINATOR_WORKING_DIR", "/tmp")
    try:
        working_dir=tempfile.mkdtemp(prefix=job+"-", dir=working_dir_parent,
                suffix="-" + str(os.getpid()))
    except:
        errorLog(notify_buf, "Kelvinator error when creating temp file in \"%s\"" % working_dir_parent)
        raise
    infoLog(notify_buf, "Working directory: " + working_dir)

    subdir = working_dir + "/" + subdir_name
    try:
        os.mkdir(subdir)
    except OSError:
        raise VideoError("cannot create \"%s\", potential collision" % subdir)
    if not os.path.isdir(subdir):
        raise VideoError("Unable to create dir: " + subdir)

    return (working_dir, subdir)


def cleanup_working_dir(notify_buf, working_dir):
    infoLog(notify_buf, "Cleaning up working dir: " + working_dir)
    dirRemove(working_dir)


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
            raise VideoError("Unable to remove dir: %s" % path)


class VideoError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)


def get_video(notify_buf, working_dir, video_filename, source_path):
    infoLog(notify_buf, "Source file: " + source_path)
    source_file = default_storage.open(source_path)
    infoLog(notify_buf, "Original file size: %s" % str(default_storage.size(source_path)))

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
        raise VideoError("file size zero, video file did not download properly")


def notify(task, notify_buf, notify_addr, prefix, suffix, filename, store_path):
    if notify_addr is None: return

    subject = "%s result: %s %s %s" % (task, prefix, suffix, filename)

    body =  "course: %s %s\n" % (prefix, suffix)
    body += "video file: %s\n" % store_path
    body += "machine: %s\n" % socket.gethostname()
    body += "\n"
    body += "-------- LOG --------\n"
    body += "\n"
    body += "\n".join(notify_buf)

    send_mail(subject, body, "noreply@class.stanford.edu", [ notify_addr, ])



