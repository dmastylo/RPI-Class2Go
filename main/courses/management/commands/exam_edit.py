from optparse import make_option
from textwrap import wrap
from collections import namedtuple
from pprint import pprint
import sys
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from c2g.models import Exam


class Command(BaseCommand):
    """
    Define the edit_exam manamagement command: bulk updates of exam settings.
    """

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
        make_option("-t", "--type", dest="examtype", type="string",
            help="Select by type, valid values are: %s" \
                    % ", ".join(sorted(exam_types))),

        # Change
        make_option("-s", "--set", action="append", dest="setlist", 
            default=[], metavar="NAME=\"VAL\"",
            help="Set this to that for every exam that matches your search. "  \
                 "Specify this multiple times to update multiple columns. " \
                 "The quotes around the value are optional."),

        # Do It!
        make_option("-u", "--update", action="store_false", dest="dryrun", default=True,
            help="actually update database (default is dry run)."),

    ) + BaseCommand.option_list


    def validate_selector(self, options):
        """
        Make sure we have a valid set of things to select on, and if we do,
        return a named tuple like this:
          Selector(exam_ids=[840, 841], course_id=11, type='survey')
        """
        if not (options['exam_ids'] or options['course_id']):
            raise CommandError("At least one of exam_ids (-e) or course_id (-c) is required.")

        Selector = namedtuple('Selector', 'exam_ids, course_id, examtype')

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

        if options['examtype']:
            if options['examtype'] not in self.exam_types:
                raise CommandError("Invalid exam type \"%s\" given, allowed types are: %s"
                    % (options['examtype'], ", ".join(sorted(self.exam_types))))

        return Selector(exam_ids=result_exam_id_list, 
                course_id=options['course_id'], 
                examtype=options['examtype'])


    def validate_setters(self, options):
        """
        Decide what we're going to set for each of the exams we select.  Returns
        a dict with columns and settings for each.
        """
        resultdict = {}

        if not options['setlist']:
            raise CommandError("you must specify at least one set (-s) command")

        for cmd in options['setlist']:
            splitcmd = cmd.split('=')
            if len(splitcmd) != 2:
                raise CommandError("cannot parse \"%s\", commands must be of the form NAME=VAL"
                        % cmd)
            (name, val) = splitcmd
            if name not in self.exam_attrs:
                raise CommandError("value \"%s\" isn't a valid property of Exam, valid values are %s"
                        % (splitcmd[0], self.exam_attrs))
            resultdict[name] = val

        return resultdict


    def handle(self, *args, **options):
        """The actual exam_edit command"""

        selector = self.validate_selector(options)
        pprint(selector)

        setter_dict = self.validate_setters(options)
        sys.stdout.write("Setters = ")
        pprint(setter_dict)
                
        exams = Exam.objects.all()
        if selector.course_id:
            exams = exams.filter(course=selector.course_id)
        if selector.exam_ids:
            exams = exams.filter(id__in=selector.exam_ids)
        if selector.examtype:
            exams = exams.filter(exam_type=selector.examtype)

        if options['dryrun']:
            matches = len(exams)
            print "dryrun matches = %d" % matches
        else:
            updates = exams.update(**setter_dict)
            print "updated = %d" % updates

        for exam in exams:
            sys.stdout.write("%d: " % exam.id)
            pprint(exam)

