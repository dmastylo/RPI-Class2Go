from django.core.management.base import BaseCommand, CommandError
from c2g.models import *
from django.contrib.auth.models import User,Group
from django.db import connection, transaction
from courses.reports.generation.gen_quiz_summary_report import *


class Command(BaseCommand):
    help = "Get quiz summary. Syntax: manage.py gen_quiz_summary_report <course_handle> <type {'video' | 'problemset'}> <quiz_slug> [save_to_s3 (1 or 0)]\n"
        
    def handle(self, *args, **options):
        if len(args) < 3:
            print "Missing course or quiz handle or quiz type!"
        
        try:
            ready_course = Course.objects.get(handle= args[0], mode='ready')
        except Course.DoesNotExist:
            print "Failed to find course with given handle"
            return

        if args[1] == 'video':
            try:
                ready_quiz = Video.objects.get(course=ready_course, slug=args[2])
            except Video.DoesNotExist:
                print "Failed to find video with given slug"
                return
        elif args[1] == 'problemset':
            try:
                ready_quiz = ProblemSet.objects.get(course=ready_course, slug=args[2])
            except ProblemSet.DoesNotExist:
                print "Failed to find problemset with given slug"
                return
        else:
            print "Second arg must be either 'video' or 'problemset'"
            return
        
        save_to_s3 = True if (len(args) > 3 and args[3] == '1') else False
        
        report = gen_quiz_summary_report(ready_course, ready_quiz, save_to_s3)
        if save_to_s3:
            if report['path']: print "Report successfully written to: %s" % report['path']
            else: print "Failed to generate report or write it to S3!"
        