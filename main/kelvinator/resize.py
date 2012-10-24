# For more info, see: http://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide

import subprocess
from celery import task
from utility import *

# ffmpeg -i INPUTFILENAME -c:v libx264 -profile:v baseline -crf 23 -c:a libfaac OUTPUTFILENAME

def scaledown(notify_buf, working_dir, target_dir, video_file, options):
    infoLog(notify_buf, "Kicking off ffmpeg, hold onto your hats")
    cmdline = [ "ffmpeg", 
                "-i", working_dir + "/" + video_file,  # input
                "-c:v", "libx264",
                "-profile:v", "baseline" \
              ] \
                + options + \
              [ "-c:a", "libfaac", 
                target_dir + "/" + video_file ]
    returncode = subprocess.call(cmdline);

    if returncode == 0:
        infoLog(notify_buf, "ffmpeg completed, returncode %d" % returncode)
    else:
        errorLog(notify_buf, "ffmpeg completed, returncode %d" % returncode)
        cleanup_working_dir(notify_buf, working_dir)
        raise VideoError("ffmpeg error %d" % returncode)


def upload(notify_buf, target_dir, target_part, prefix, suffix, video_id, video_file, store_loc):
    # I wish Filesystem API worked the same for local and remote, but it don't
    if store_loc == 'local':
        root = getattr(settings, 'MEDIA_ROOT')
        store_path = root + "/" + prefix + "/" + suffix + "/videos/" + str(video_id) + "/" + target_part
        if default_storage.exists(store_path):
                dirRemove(store_path) 
        os.mkdir(store_path)
    else:
        store_path = prefix + "/" + suffix + "/videos/" + str(video_id) + "/" + target_part
        default_storage.delete(store_path)

    local_file = open(target_dir + "/" + video_file, 'rb')
    store_file = default_storage.open(store_path + "/" + video_file, 'wb')
    store_file.write(local_file.read())
    local_file.close()
    store_file.close()


@task()
def resize(store_path_raw, target_raw, notify_addr=None):
    """
    Given a video path, scale it down and save the result alongside the original
    video.  So we can provide different download options.

    Preset is either "small" or "large".
    """

    notify_buf = []

    target = target_raw.lower()
    if target != "small" and target != "large":
        VideoError("Target size must either be \"large\" or \"small\", got \"%s\"" % target)

    (store_path, course_prefix, course_suffix, video_id, video_file) = splitpath(store_path_raw)

    store_loc = 'remote'
    if getattr(settings, 'AWS_ACCESS_KEY_ID') == 'local':
        store_loc = 'local'

    work_dir = None
    try:
        (work_dir, smaller_dir) = create_working_dirs("resize", notify_buf, target)
        get_video(notify_buf, work_dir, video_file, store_path)
        if target == "large":
            options = [ "-b:v", "100k" ]
        else:
            options = [ "-b:v", "100k", "-s", "wvga" ]
        scaledown(notify_buf, work_dir, smaller_dir, video_file, options)
        upload(notify_buf, smaller_dir, target, course_prefix, course_suffix, video_id, video_file, store_loc)

    except:
        if work_dir: cleanup_working_dir(notify_buf, work_dir)
        notify("Resize (%s)" % target, notify_buf, notify_addr, course_prefix, course_suffix, 
               video_file, store_path)
        raise

    cleanup_working_dir(notify_buf, work_dir)
    notify("Resize (%s)" % target, notify_buf, notify_addr, course_prefix, course_suffix, 
           video_file, store_path)

