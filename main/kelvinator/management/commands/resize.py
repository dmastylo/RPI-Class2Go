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
    args="<size> <prefix> <suffix> <slug>"
    help="""    Convert the video to a smaller size and store result in a directory right alongside
    the video.

    Arguments:
        size       'large' or 'small'
        prefix     course short name, like "nlp"
        suffix     the term, like "Fall2012"
        slug       URL parameter for the video, like "lecture1"
    """

    option_list = (
        make_option("-l", "--local", dest="force_local", action="store_true", default=False,
                    help="Force run locally"),
        make_option("-r", "--remote", dest="force_remote", action="store_true", default=False,
                    help="Force run remote (queued)"),
        make_option("-n", "--notify", dest="notify_addr",  
                    help="Send mail to address when done"),
    ) + BaseCommand.option_list
        
    def handle(self, *args, **options):
        if len(args) != 4:
            raise CommandError("Wrong number of arguments, %d instead of 4" % len(args))
        if options['force_local'] and options['force_remote']:
            raise CommandError("Can't run both local and remote")
        target=args[0]
        arg_prefix=args[1]
        arg_suffix=args[2]
        handle=arg_prefix+"--"+arg_suffix
        slug=args[3]

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
            
        # FIXME: after confirming this works, remove these lines
        #where = getattr(settings, 'AWS_ACCESS_KEY_ID', 'local')
        #if options['force_local']: 
        #    where='local'
        #if options['force_remote']:
        #    where='remote'
        #if where == 'local':
        if (is_storage_local() or options['force_local']) and not options['force_remote']:
            media_root = getattr(settings, 'MEDIA_ROOT')
            local_path = media_root + "/" + video.file.name
            kelvinator.tasks.resize(local_path, target, options['notify_addr'])
            print "Resize complete: %s" % video.file.name
        else:
            kelvinator.tasks.resize.delay(video.file.name, target, options['notify_addr'])
            print "Resize queued (%s): %s" % (instance, video.file.name)



