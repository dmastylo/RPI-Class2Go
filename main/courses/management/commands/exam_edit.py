try:
    from dateutil import parser
except ImportError, msg:
    parser = False
from optparse import make_option
import inspect
from textwrap import wrap
from collections import namedtuple

from django.core.management.base import BaseCommand, CommandError
from c2g.models import Exam

class Command(BaseCommand):

    # instantiate a dummy exam so we can inspect it
    testexam=Exam()
    exam_attrs = [a for a in vars(testexam) \
                    if not callable(getattr(testexam,a)) \
                    and not a.startswith('_')]
    exam_types = [t[0] for t in Exam.EXAM_TYPE_CHOICES]

    help = "Make bulk exam changes. With the -u option update the database. " \
            " PLEASE BE CAREFUL." \
            "\n\nSelect which exams to change with one or more of " \
            "-e, -c, and -t. At least one of -e or -c must be used." \
            "\n\nThe list of Exam columns are:\n%s" % "\n".join(wrap(", ".join(sorted(exam_attrs))))

    option_list = (
        # Select
        make_option("-e", "--examids", dest="exam_ids", type="string",
            help="Select by comma-separated list of exam ID's"),
        make_option("-c", "--courseid", dest="course_id", type="int", 
            help="Select by course.  If only this option is chosen, all exams " \
                    "for that course will be selected."),
        make_option("-t", "--type", dest="type", type="string",
            help="Select by type, valid values are: %s" \
                    % ", ".join(sorted(exam_types))),

        # Change
        make_option("-s", "--set", action="append", dest="setlist", 
            default=[], metavar="COL=\"VAL\"",
            help="Set this to that for every exam that matches your search. "  \
                 "Specify this multiple times to update multiple columns. " \
                 "The quotes around the value are optional."),

        # Do It!
        make_option("-u", "--update", action="store_false", dest="dryrun", default=True,
            help="actually update database (default is dry run)."),

    ) + BaseCommand.option_list

#        make_option("--start", dest="start_time",
#            help="consider entries no earlier than X, eg \"2/17/2013\" or \"1/1/2012 14:40\". We use the python dateutil parser on dates, see http://labix.org/python-dateutil"),
#        make_option("--end", dest="end_time",
#            help="consider entries no later than X"),

    def validate_options(self, options):
        """
        Validate options and parse into useful data types. Returns a namedtuple.
        """
        if not (options['exam_ids'] or options['course_id']):
            raise CommandError("At least one of exam_ids (-e) or course_id (-c) is required.")

        Selector = namedtuple('Selector', 'exam_ids, course_id, type')

        result_exam_id_list = []
        if options['exam_ids']:
            exid_strings = options['exam_ids'].split(',')
            for exid_str in exid_strings:
                errstr = None
                try:
                    exid = int(exid_str)
                    if exid == 0:
                        errstr = "exam id \"%s\" is invalid"
                except ValueError as e:
                    errstr = e
                if errstr:
                    raiseCommandError("Exam ID parsing error, %s" % errstr)
                result_exam_id_list.append(exid)

        result_type = None
        if options['type']:
            if options['type'] not in self.exam_types:
                raise CommandError("Invalid exam type \"%s\" given, allowed types are: %s"
                    % (options['type'], ", ".join(sorted(self.exam_types))))
            result_type = options['type']

        return Selector(exam_ids=result_exam_id_list, 
                course_id=options['course_id'], 
                type=result_type)


    def handle(self, *args, **options):
        sel = self.validate_options(options)


        
