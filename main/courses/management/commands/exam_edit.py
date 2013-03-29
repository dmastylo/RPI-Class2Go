try:
    from dateutil import parser
except ImportError, msg:
    parser = False
from optparse import make_option
import inspect
from textwrap import wrap

from django.core.management.base import BaseCommand, CommandError
from c2g.models import Exam

class Command(BaseCommand):

    # instantiate a dummy exam so we can inspect it
    testexam=Exam()
    exam_attrs = [a for a in vars(testexam) \
                    if not callable(getattr(testexam,a)) \
                    and not a.startswith('_')]

    help = "Make bulk exam changes. With the -u option update the database. PLEASE BE CAREFUL." \
        "\n\nThe list of Exam columns are:\n%s" % "\n".join(wrap(", ".join(sorted(exam_attrs))))

    option_list = (
        make_option("-u", "--update", action="store_false", dest="dryrun", default=True,
            help="actually update database (default is dry run)."),
        make_option("-s", "--set", action="append", dest="setlist", 
            default=[], metavar="COL=\"VAL\"",
            help="Set this to that for every exam that matches your search. "  \
                 "Specify this multiple times to update multiple columns. " \
                 "The quotes around the value are optional."),
    ) + BaseCommand.option_list

#        make_option("--start", dest="start_time",
#            help="consider entries no earlier than X, eg \"2/17/2013\" or \"1/1/2012 14:40\". We use the python dateutil parser on dates, see http://labix.org/python-dateutil"),
#        make_option("--end", dest="end_time",
#            help="consider entries no later than X"),

    def handle(self, *args, **options):
        pass

