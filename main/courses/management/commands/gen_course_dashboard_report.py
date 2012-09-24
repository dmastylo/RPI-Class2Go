from django.core.management.base import BaseCommand, CommandError
from c2g.models import *
from django.contrib.auth.models import User,Group
from django.db import connection, transaction
from courses.reports.generation.course_dashboard import *

class Command(BaseCommand):
    help = "Get course dashboard stats\n"
        
    def handle(self, *args, **options):
        if len(args) == 0:
            print "No course handle supplied!"
            
        try:
            course = Course.objects.get(handle= args[0], mode='draft')
        except:
            print "Failed to find course with given handle"
            return
            
        print gen_course_dashboard_report(course)