from collections import defaultdict, namedtuple
import json
import logging
from optparse import make_option
import os
try:
    import pdfkit
except ImportError, msg:
    pdfkit = False
import pprint
import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from c2g.models import Course, CourseCertificate, CourseStudentScore, UserProfile
import settings
from tools.certificates import tasks as cert_tasks


logger = logging.getLogger(__name__)
GLOBAL_DEBUG = False


def debug_out(s):
    sys.stdout.write(s + '\n')

class TemplateCache(object):
    """In-memory cache of certificate template strings loaded off disk."""
    def __init__(self):
        self.__templates = {}

    def get(self, asset_prefix, asset_path, cert_type):
        """Return the string containing the unrendered template"""
        # probably not necessary if we use a defaultdict?
        if (asset_prefix, asset_path, cert_type) not in self.__templates:
            infile_name = 'certificate-' + cert_type + '.html'
            if not asset_prefix: asset_prefix = getattr(settings, 'MEDIA_ROOT', '/')
            infile_path = os.path.join(asset_prefix, asset_path, infile_name)
            template_file = open(infile_path, 'rb')
            unrendered_template = template_file.read()
            template_file.close()
            self.__templates[(asset_prefix, asset_path, cert_type)] = unrendered_template
            if GLOBAL_DEBUG: debug_out("Caching template for %s, %s, %s" % (asset_prefix, asset_path, cert_type))
            return unrendered_template
        else:
            return self.__templates[(asset_prefix, asset_path, cert_type)]


class CertificateCache(object):
    """In-memory cache of certificate metadata loaded from the database.

    Also, creates certificate entries in the database if they do not exist."""
    def __init__(self):
        self.__certs = {}

    def get(self, course, type_tag):
        """Return the CourseCertificate database entry for this course and type."""
        # unnecessary if we use a defaultdict?
        # except we'd still need a bit of structure to instantiate missing certs
        if (course, type_tag) not in self.__certs:
            assets_path = os.path.join(course.prefix, course.suffix, 'certificates', 'assets')
            storage_path = os.path.join(course.prefix, course.suffix, 'certificates', 'storage')
            (certificate_info, create_status) = CourseCertificate.objects.get_or_create(course=course, assets=assets_path, storage=storage_path, type=type_tag)
            self.__certs[(course, type_tag)] = certificate_info
            if GLOBAL_DEBUG: debug_out("Caching cert for %s, %s" % (course.handle, type_tag))
            return certificate_info
        else:
            return self.__certs[(course, type_tag)]


class Command(BaseCommand):
    args = "<course_handle> <no_cert_file> <cert_conditions_file>"
    help = """Statement the students for a specified course handle

Parameter course_handle is, unsurprisingly, the course_handle for the course to
be processed, i.e., 'db--winter2013'.
    
File no_cert_file is a newline-delimited list of usernames who should never be
given statements (for example, admin users and cheaters). For example, it may
look like:
    ---begin sample no_cert_file.txt
    admin
    another-admin
    cheater@example.com
    BadAlicePoorBob
    ---end sample no_cert_file.txt

File cert_conditions_file is a json-formatted list of dictionaries, processed
in order for each student in a course. The first dictionary that matches the
student will be used and no subsequent ones. Each dictionary is a set of 
certifications (keys) and the tests that determine whether they apply (values).
They are applied with equal weighting, so if several certifications within one
dictionary apply to a user, the user will get all of those certifications. To
make different certifications mutually exclusive, put them in different
dictionaries. The tests portion of a dictionary entry (values) consists of a
list containing lists of exactly 2 items. These two-item sublists are ANDed 
together. That is a given certification (dictionary key) will be given to a
student only if every test in the test list (dictionary value) passes. The
format of the 2-item sublists consists of a score tag as used by the Aggregator
and a fractional value indicating what proportion of the available points must
be earned.

To clarify, here are some examples:
    This example file has three mutually-distinct conditions:
      'no cert', which is implicit
      'distinction', which happens when the student has a 75% on exercises
                     tagged by the aggregator as 'accomplishment' AND has 50%
                     on exercises tagged by the aggregator as 
                     'challenge-exercises'
    ---begin first cert_conditions_file example
    [{'distinction':[['accomplishment', 0.75], ['challenge-exercises', 0.50]]},{'accomplishment': [['accomplishment', 0.50]]}]
    ---end first cert_conditions_file example

    In this example, 'distinction' and 'accomplishment' can be achieved without
    mutual exclusion:
    ---begin second cert_conditions_file example
    [{'distinction':[['accomplishment', 0.75], ['challenge-exercises', 0.50]], 'accomplishment': [['accomplishment', 0.50]]}]
    ---end second cert_conditions_file example
    
    The PDFKti library has a number of system dependencies which cannot be
    installed from pip. Please check the tools/certificates/README_WKHTML.md
    and README_SETUP.md for additional notes.
    """
    option_list = ( 
                   make_option('-s', '--single', dest='single_student', default="", help="Force run on only <single_student>"),
                   make_option('-P', '--skip-pdf', dest='skip_pdf', action="store_true", default=False, help="Skip PDF generation and attachment"),
                   make_option('-D', '--debug', dest='DEBUG', action="store_true", default=False, help="Describe everything as it happens"),
                  ) + BaseCommand.option_list

    def handle(self, *args, **options):
        # Option processing
        if len(args) != 3:
            raise CommandError("Wrong number of arguments, %d instead of 3" % len(args))
        if not pdfkit:
            raise CommandError("Can't issue certificates without python library pdfkit installed")
        course_handle = args[0].strip()
        no_cert_file  = args[1].strip()
        cert_conditions_file = args[2].strip()
        single_student = None
        single_student_username = options.get('single_student', '')
        if single_student_username:
            single_student = User.objects.get(username=single_student_username)
        global GLOBAL_DEBUG
        if options['DEBUG']:
            GLOBAL_DEBUG = True
        if GLOBAL_DEBUG: debug_out("Option processing complete, memoizing working objects")

        # Working object memoization
        if len(course_handle) == 0:
            raise CommandError("Bad course handle: '%s'" % course_handle)
        if len(no_cert_file) == 0:
            raise CommandError("Bad no_cert_file: '%s'" % no_cert_file)
        if len(cert_conditions_file) == 0:
            raise CommandError("Bad cert_conditions_file: '%s'" % cert_conditions_file)
        try:
            course = Course.objects.get(handle=course_handle, mode='ready')
        except:
            raise CommandError("Bad course handle or could not retrieve course '%s'" % course_handle)
        if GLOBAL_DEBUG: debug_out("Loaded course metadata for %s" % course.handle)

        donotcertify = set()
        with open(no_cert_file) as nocertfile:
            # See also documented no_cert_file format at EOF
            donotcertify = set((username.strip() for username in nocertfile.readlines()))
        if GLOBAL_DEBUG: debug_out("Loaded 'do not certify' list %s" % no_cert_file)

        with open(cert_conditions_file) as binning_desc:
            tmp_str = binning_desc.read()
            binning = json.loads(tmp_str)
        if GLOBAL_DEBUG: debug_out("Loaded 'certification conditions' file %s" % cert_conditions_file)

        def __all_students(course):
            debug_counter = 0
            for student in course.get_all_students():
                debug_counter += 1
                if debug_counter % 100 == 0:
                    print debug_counter
                #if GLOBAL_DEBUG and debug_counter % 100 == 0: debug_out(str(debug_counter))
                yield student
        def __one_student(course):
            if GLOBAL_DEBUG: debug_out("Processing single student %s" % single_student.username)
            yield single_student
        student_generator = __all_students if not single_student_username else __one_student

        def __apply_test(test, subtotals_d):
            """A 'test' is a pair like ['scoring tag', percentage_that_passes]"""
            # See also documented cert_conditions_file format at EOF
            #testscore = subtotals_d[test[0]]
            #                       forces failure on missing key
            testscore = subtotals_d.get(test[0], (0, 100)) 
            #       score           total       test multiplier
            return testscore[0] >= (testscore[1] * test[1])

        templates = TemplateCache()
        certificates = CertificateCache()
        if GLOBAL_DEBUG: debug_out("Memoization of working objects complete, processing students")
        
        # assign certificates and generate assets
        got_certs = defaultdict(int)
        for student in student_generator(course):
            if student.username in donotcertify:
                # log a message and move to the next student
                logger.info("class2go statement generation: %s skipped for entry in no_cert_file %s" % (student.username, no_cert_file))
                continue
            subtotals_d = {}
            subtotals = CourseStudentScore.objects.filter(course=course, student=student).values_list('tag', 'score', 'total')
            for sub in subtotals:
                subtotals_d[sub[0]] = (sub[1], sub[2])
            # ok now do the binning for real
            earned_certs = set()
            for cert_set in binning:
                for certificate_type, tests in cert_set.iteritems():
                    if reduce(lambda x,y: x and y, (__apply_test(test, subtotals_d) for test in tests)):
                        earned_certs.add(certificate_type)
                        got_certs[certificate_type] += 1
                if earned_certs:
                    break
            if not earned_certs:
                got_certs['none'] += 1

            # ok now actually assign the cert object and run pdf generation
            profile = UserProfile.objects.get(user=student)
            for cert in earned_certs:
                cert_info = certificates.get(course, cert)

                # Attach "platonic" certification to user's profile
                profile.certificates.add(cert_info)
                profile.save() 

                if not options['skip_pdf']:
                    # Fire off worker task to build the pdf and upload it to s3
                    cert_prefix = ''
                    templatestr = templates.get(cert_prefix, cert_info.assets, cert_info.type)
                    context_d = {}
                    for k,v in subtotals_d.iteritems():
                        context_d[k.replace('-','_')] = v
                    celery_job = cert_tasks.makePDF.delay(templatestr, cert_prefix, course, cert_info, student, context_in=context_d)
                    if GLOBAL_DEBUG: debug_out("Attached PDF for %s at %s" % (student.username, celery_job))

        print "Certification process complete. Stats:"
        pprint.pprint(got_certs)


#########################################################
# This is an example no_certs_file: it consists of a newline-delimeted list of usernames
# of students who should never receive certificates for this course
#########################################################
#BAD_PERSON_USERNAME
#cheater@example.com
#admin

#########################################################
# This is an example cert_conditions_file with inline comments to help you understand 
# how it works
#########################################################
#
#/* This is an ordered list. The first one that has any dictionary value match
# * is the one that will be used. */
#[
#    /* This is a dictionary of a set of certification conditions which may be
#     * obtained simultaneously. If your various certification conditions are
#     * mutually exclusive, then there will be several dictionaries with only one
#     * key/value pair each. */
#                       /* this is a list of clauses which get ANDed together */
#                                                  /* aggregator tag name */
#                                       /* % of max */
#    {'distinction':    [['accomplishment', 0.75], ['challenge-exercises', 0.50]],},
#    {'accomplishment': [['accomplishment', 0.50],],},
#]
#
# Except of course you can't have trailing commas or comments or excess 
# whitespace in your json, so to be valid you'd have to write it like:
#[{'distinction':[['accomplishment', 0.75], ['challenge-exercises', 0.50]]},{'accomplishment': [['accomplishment', 0.50]]}]
