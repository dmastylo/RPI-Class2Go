from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import MultipleObjectsReturned
from c2g.models import Video
import urllib
from django.db import connection, transaction
import kelvinator.tasks 
from django.conf import settings

bucket=getattr(settings, 'AWS_STORAGE_BUCKET_NAME')

class Command(BaseCommand):
    args="<prefix> <suffix> <video_slug> <key_frames>"
    help="Runs the Kelvinator on a video given its course info (prefix and suffix) and slug.\n" + \
        "All parameters are case sensitive \n" + \
        "\n" + \
        "Usage: manage.py kelvinate <prefix> <suffix> <video_slug>\n" + \
        "    prefix         generally the short name, like \"nlp\"\n" + \
        "    suffix         the term, like \"Fall2012\"\n" + \
        "    video_slug     slug, like \"regexp\"\n" + \
        "    key_frames     target number of key frames per minute (default=2)" 
        
    def handle(self, *args, **kwargs):
        if len(args) < 3 or len(args) > 4:
            raise CommandError("Wrong number of arguments")
        arg_prefix=args[0]
        arg_suffix=args[1]
        handle=arg_prefix+"--"+arg_suffix
        slug=args[2]

        try:
            video = Video.objects.get(course__handle=handle, slug=slug, mode='draft')
        except MultipleObjectsReturned:
            print "Found multiple videos named \"%s\"" % slug
            return
        except Video.DoesNotExist:
            print "Video \"%s\" not found for handle \"%s\"" % (slug, handle)
            return

        if video.file.name == "default":
            print "Video slug \"%s\" doesn't have a file listed in S3 (name=\"default\")" % slug
            return
            
        s3_path="https://s3-us-west-2.amazonaws.com/"+bucket+"/"+urllib.quote_plus(video.file.name,"/")
        
        keyframes_per_minute = 2
        if len(args) > 3:
            keyframes_per_minute = args[3]
        
        kelvinator.tasks.kelvinate(s3_path, keyframes_per_minute)
        
        print "Kelvination complete"

