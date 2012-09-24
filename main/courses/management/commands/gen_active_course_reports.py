from django.core.management.base import BaseCommand, CommandError
from c2g.models import *
from django.contrib.auth.models import User,Group
from django.db import connection, transaction
from courses.reports.generation.course_dashboard import *
from courses.reports.generation.course_quizzes import *
from datetime import datetime


class Command(BaseCommand):
    help = "Generates course_dashboard and course_quizzes reports _for_courses_that_are_currently_active_ (Between their start and end date). Syntax: manage.py gen_active_course_reports\n"
        
    def handle(self, *args, **options):
        now = datetime.now()
        active_courses = Course.objects.filter(mode='ready', calendar_start__lt=now, calendar_end__gt=now)
        for ready_course in active_courses:
            gen_course_dashboard_report(ready_course.image, save_to_s3=True)
            gen_course_quizzes_report(ready_course, save_to_s3=True)