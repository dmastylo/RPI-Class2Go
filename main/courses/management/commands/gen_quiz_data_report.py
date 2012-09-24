from django.core.management.base import BaseCommand, CommandError
from c2g.models import *
from django.contrib.auth.models import User,Group
from django.db import connection, transaction
from courses.reports.generation.quiz_data import *


class Command(BaseCommand):
    help = "Get quiz attempts data. Syntax: manage.py gen_quiz_attempts_report <course_handle> <type {'video' | 'problemset'}> <quiz_slug> <order_by={['time'] | 'student'}>\n"
        
    def handle(self, *args, **options):
        if len(args) < 3:
            print "Missing course or quiz handle or quiz type!"
        
        try:
            ready_course = Course.objects.get(handle= args[0], mode='ready')
        except:
            print "Failed to find course with given handle"
            return
        
        if args[1] == 'video':
            try:
                ready_quiz = Video.objects.get(course=ready_course, slug=args[1])
            except:
                print "Failed to find video with given slug"
                return
        elif args[1] == 'problemset':
            try:
                ready_quiz = ProblemSet.objects.get(course=ready_course, slug=args[2])
            except:
                print "Failed to find problemset with given slug"
                return
        else:
            print "Second arg must be either 'video' or 'problemset'"
            return
        
        order_by = 'time_created'
        if (len(args) == 4) and (args[3] == 'student'): order_by = 'student'
        
        print gen_quiz_data_report(ready_course, ready_quiz, order_by)