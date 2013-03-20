try:
    from dateutil import parser
except ImportError, msg:
    parser = False
import string
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from c2g.models import ExamRecord, Exam, ExamScore, ExamRecordScore
from courses.exams.autograder import *
from courses.exams.views import compute_penalties

class Command(BaseCommand):
    args = "<course_id> <formula_file> <tag>"
    help = "Aggregates assessment scores (ExamScore) for course <course_id> according\nto the formula specified in <formula_file>.\nStore results for each student tagged with <tag> if not a dry-run."

    option_list = (
        make_option("-u", "--update", action="store_false", dest="dryrun", default=True,
            help="writes database (default is dry run)"),
    ) + BaseCommand.option_list

    def handle(self, *args, **options):
        if len(args) != 3:
           raise CommandError("Wrong number of arguments.  Should be exactly 3: <course_id> <formula_file> <tag>")


