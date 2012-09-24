from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import MultipleObjectsReturned
from c2g.models import Video
import urllib
from django.db import connection, transaction
import kelvinator.tasks 
from django.conf import settings
from optparse import make_option

bucket=getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
instance=getattr(settings, 'INSTANCE')

class Command(BaseCommand):
    help="Runs the Kelvinator on a video given its course info (prefix and suffix) and slug.\n" + \
        "All parameters are case sensitive \n" + \
        "\n" + \
        "Usage: manage.py kelvinate [options] <prefix> <suffix> <video_slug>\n" + \
        "    prefix         generally the short name, like \"nlp\"\n" + \
        "    suffix         the term, like \"Fall2012\"\n" + \
        "    video_slug     slug, like \"regexp\"\n" 

    option_list = (
        make_option("-r", "--remote", dest="remote", action="store_true",
                    help="do kelvination remotely (default is local)"),
        make_option("-f", "--frames", dest="target_frames", default=2, type="int",
                    help="Target number of thumbnails per minute (default=2)"),
    ) + BaseCommand.option_list
        
    def handle(self, *args, **options):
        if len(args) != 3:
            raise CommandError("Wrong number of arguments, %d instead of 3" % len(args))
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
        if len(args) > 5:
            keyframes_per_minute = args[5]
        
        if options['remote']:
            kelvinator.tasks.kelvinate.delay(s3_path, keyframes_per_minute)
            print "Kelvination queued (%s): %s" % (instance, s3_path)
        else:
            kelvinator.tasks.kelvinate(s3_path, keyframes_per_minute)
            print "Kelvination complete"


