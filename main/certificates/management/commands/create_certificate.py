from django.core.management.base import BaseCommand, CommandError

from c2g.models import Course, CourseCertificate


class Command(BaseCommand):
    args = "<course_handle> [<certificate_type>]"
    help = """ 
        Create a new statement of accomplishment for this course,type pair.

        <course_handle> is required and expects an input like 'networking--2012'
        <certificate_type> is optional, and defaults to 'completion'.

        This does not actually ensure that you have the assets necessary to issue
        the new statement; see also the command 'get_cert_assets'.
        """

    def handle(self, *args, **options):
        course_handle = ''
        cert_type = ''
        if len(args) < 1:
            raise CommandError("You must specify at least a course handle for certificate creation.")
        course_handle = args[0].strip()
        if len(args) == 1:
            cert_type = 'completion'
        elif len(args) > 2:
            raise CommandError("Too many arguments, %d" % len(args))
        else:
            cert_type = args[1].strip()

        try:
            course = Course.objects.get(handle=course_handle, mode='ready')
        except:
            raise CommandError("Bad course handle or could not retrieve course '%s'" % course_handle)

        cert = CourseCertificate.objects.filter(course=course, type=cert_type)
        if cert:
            raise CommandError("Course %s already has a certificate of type %s" % (course_handle, cert_type))

        cert = CourseCertificate.create(course=course, type=cert_type)
        
        print "%s creation complete for %s.. OK!" % (str(cert), course.title)

