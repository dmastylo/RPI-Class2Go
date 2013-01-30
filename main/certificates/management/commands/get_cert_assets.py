import os
from storages.backends.s3boto import S3BotoStorage

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


release_storage = S3BotoStorage(bucket=settings.AWS_RELEASE_BUCKET_NAME, access_key=settings.AWS_ACCESS_KEY_ID, secret_key=settings.AWS_SECRET_ACCESS_KEY)


def _mkdir(newdir):
    if os.path.isdir(newdir):
        return
    elif os.path.isfile(newdir):
        raise CommandError("Couldn't make directory %s; a file with the same name as '%s' already exists." % (newdir, newdir))
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        if tail:
            os.mkdir(newdir)
    return

def get_files_to_copy():
    to_copy = []
    sections = {}
    courses = release_storage.listdir('/certificates')[0]
    for course in courses:
        sections[course] = release_storage.listdir('/certificates/'+course)[0]
        for section in sections[course]:
            fullpath = os.path.join('/certificates', course, section, 'certificates', 'assets')
            files = release_storage.listdir(fullpath)[1]
            for filename in files:
                if not filename:
                    continue
                to_copy.append(os.path.join(fullpath, filename))
    return to_copy

def copy_file(bucket_path):
    local_dir = settings.MEDIA_ROOT
    tmp_file = release_storage.open(bucket_path, 'rb')
    local_filepath = local_dir + bucket_path[13:]  # trim off leading /certificates
    making_target, filename = os.path.split(local_filepath)
    _mkdir(making_target)
    local_file = open(local_filepath, 'wb') 
    local_file.write(tmp_file.read())
    tmp_file.close()
    local_file.close()
    return local_filepath

class Command(BaseCommand):
    args = ""
    help = """ 
        Connect to the Release bucket in S3 and copy down certificate assets
        to localhost.
        """
    def handle(self, *args, **options):
        filelist = get_files_to_copy()
        for filename in filelist:
            print "Downloading %s..." % filename, 
            local_filename = copy_file(filename)
            print " done.\n    Saved as %s" % local_filename

