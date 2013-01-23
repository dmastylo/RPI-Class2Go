from optparse import make_option

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand, CommandError

from c2g.models import Video
from c2g.util import is_storage_local
import kelvinator.tasks 


bucket=getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
instance=getattr(settings, 'INSTANCE')


class Command(BaseCommand):
    args="<prefix> <suffix> <slug>"
    help="""    Extract thumbnail images for a video given its course info (prefix
    and suffix) and slug.  All parameters are case sensitive.  Will
    decide to run local or remote (queued) based on your AWS settings
    in your database.py file, unless you override.

    Arguments:
        prefix     course short name, like "nlp"
        suffix     the term, like "Fall2012"
        slug       URL parameter for the video, like "lecture1"
    """

    option_list = (
        make_option("-l", "--local", dest="force_local", action="store_true", default=False,
                    help="Force run locally"),
        make_option("-r", "--remote", dest="force_remote", action="store_true", default=False,
                    help="Force run remote (queued)"),
        make_option("-f", "--frames", dest="target_frames", default=2, type="int",
                    help="Target number of thumbnails per minute (default=2)"),
        make_option("-n", "--notify", dest="notify_addr",  
                    help="Send mail to address when done"),
    ) + BaseCommand.option_list
        
    def handle(self, *args, **options):
        if len(args) != 3:
            raise CommandError("Wrong number of arguments, %d instead of 3" % len(args))
        if options['force_local'] and options['force_remote']:
            raise CommandError("Can't run both local and remote")
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
            
        if (is_storage_local() or options['force_local']) and not options['force_remote']:
            media_root = getattr(settings, 'MEDIA_ROOT')
            local_path = media_root + "/" + video.file.name
            kelvinator.tasks.kelvinate(local_path, options['target_frames'], options['notify_addr'])
            print "Kelvination complete: %s" % video.file.name
        else:
            kelvinator.tasks.kelvinate.delay(video.file.name, options['target_frames'], options['notify_addr'])
            print "Kelvination queued (%s): %s" % (instance, video.file.name)


