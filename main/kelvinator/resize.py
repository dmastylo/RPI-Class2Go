# For more info, see: 
# - http://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide
# size abbreviations: 
# - http://linuxers.org/tutorial/how-extract-images-video-using-ffmpeg

import subprocess
from celery import task
from utility import *

# video sizes we support: key is size name (used for target subdirectory) and value
# are the parameters (as a list) that we'll pass to ffmpeg.
sizes = { "large":  [ "-crf", "23", "-s", "1280x720" ],   # original size, compressed
          "medium": [ "-crf", "27", "-s", "wvga" ],       # wvga = 852x480 at 16:9
          "small":  [ "-crf", "30", "-s", "320x180" ],    # 320p at 16:9
          "tiny":   [ "-crf", "40", "-s", "320x180" ],
        }

common_ffmpeg_options = [ "-c:v", "libx264",             # video codec
                          "-profile:v", "baseline",      # most compatible
                          "-c:a", "libfaac",             # audio codec
                        ]

def scaledown(notify_buf, working_dir, target_dir, video_file, target_size):
    infoLog(notify_buf, "Kicking off ffmpeg, hold onto your hats")
    cmdline = [ "ffmpeg", "-i", working_dir + "/" + video_file, ] \
                + common_ffmpeg_options  \
                + sizes[target_size] \
                + [ target_dir + "/" + video_file ]
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
        scaledown(notify_buf, work_dir, smaller_dir, video_file, target)
        upload(notify_buf, smaller_dir, target, course_prefix, course_suffix, video_id, video_file, store_loc)

    except:
        if work_dir: cleanup_working_dir(notify_buf, work_dir)
        notify("Resize (%s)" % target, notify_buf, notify_addr, course_prefix, course_suffix, 
               video_file, store_path)
        raise

    cleanup_working_dir(notify_buf, work_dir)
    notify("Resize (%s)" % target, notify_buf, notify_addr, course_prefix, course_suffix, 
           video_file, store_path)

