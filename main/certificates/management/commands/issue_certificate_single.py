from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse

from c2g.models import Course, CourseCertificate, UserProfile
from c2g.util import get_site_url, is_storage_local
import certificates.tasks


def notify(cert_type, firstname, lastname, notify_addr, prefix, suffix):
    if not notify_addr or notify_addr == '(none specified)': return False
    subject = 'Your %s statement of accomplishment of %s is now available' % (prefix, cert_type)
    body = "Congratulations %s %s, you have earned a statement of accomplishment of %s " % (firstname, lastname, cert_type)
    body += "in the course %s, section %s.\n" % (prefix, suffix)
    body += "\nYou can download the PDF from your profile page at %s.\n" % (get_site_url()[:-1] + reverse('accounts.views.profile'))
    send_mail(subject, body, "noreply@class.stanford.edu", [ notify_addr, ])
    return True


class Command(BaseCommand):
    args = "<course_handle> <username>"
    help = """ 
        Issue a statement of accomplishment for the course referred to by
        course_handle to the user registered as username. If type
        is specified, creates that style of statement (e.g., 'completion' vs.
        'distinction').
        """
    option_list = ( 
                   make_option('-t', '--type', dest='cert_type', default="completion", help="Specify certificate type to generate"),
                   make_option('-l', '--local', dest='force_local', action="store_true", default=False, help="Force run locally"),
                   make_option('-r', '--remote', dest='force_remote', action="store_true", default=False, help="Force run remote (queued)"),
                   make_option('-E', '--email-test', dest='email_test', action="store_true", default=False, help="Send notification to admin"),
                   make_option('-e', '--email-notify', dest='email_user', action='store_true', default=False, help="Send notification to <username>"),
                  ) + BaseCommand.option_list

    def handle(self, *args, **options):
        # Option processing
        if len(args) != 2:
            raise CommandError("Wrong number of arguments, %d instead of 2" % len(args))
        if options['force_local'] and options['force_remote']:
            raise CommandError("Can't run both local and remote.")
        course_handle = args[0].strip()
        username      = args[1].strip()
        if len(username) == 0:
            return
        
        # Working object memoization
        if len(course_handle) == 0:
            raise CommandError("Bad course handle: '%s'" % course_handle)
        try:
            course = Course.objects.get(handle=course_handle, mode='ready')
        except:
            raise CommandError("Bad course handle or could not retrieve course '%s'" % course_handle)

        certificate_info = CourseCertificate.objects.get(course=course, type=options['cert_type'])
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)

        # Fire off worker task
        cert_prefix = ''
        if (is_storage_local() or options['force_local']) and not options['force_remote']:
            cert_prefix = getattr(settings, 'MEDIA_ROOT', '')
        cert_path = certificates.tasks.certify(cert_prefix, course, certificate_info, user)
        #print "Certification complete: %s" % cert_path
        print "Certification complete: %s" % certificate_info.dl_link(user)

        # Attach new certification to user's profile
        profile.certificates.add(certificate_info)
        profile.save() 
        print "Certificate attached to profile of %s" % user.username

        # Send user notifications (if applicable)
        if options['email_test'] and options['email_user']:
            raise CommandError("Can't notify both admin and %s" % username)
        to_email = '(none specified)'
        if options['email_test']:
            admins = getattr(settings, 'ADMINS', False)
            if admins:
                to_email = admins[0][1]
        elif options['email_user']:
            to_email = user.email
        if notify(certificate_info.type, user.first_name, user.last_name, to_email, course.prefix, course.suffix):
            print "Notification for %s sent to %s." % (username, to_email)
        else: 
            print "No notification sent to %s at address %s." % (username, to_email)
