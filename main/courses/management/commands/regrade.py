#!/usr/bin/env python

from optparse import make_option
from dateutil import parser

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from c2g.models import ExamRecord, Exam
from courses.exams.autograder import *

class Command(BaseCommand):
    args = "<exam id>"
    help = "Grade all records for an exam and report ones that are inconsistent"

    option_list = (
        make_option("-u", "--update", action="store_false", dest="dryrun", default=True,
            help="update regraded rows in database (default is dry run)"),
        make_option("--start", dest="start_time",
            help="consider entries no earlier than X, eg \"2/17/2013\" or \"1/1/2012 14:40\". We use the python dateutil parser on dates, see http://labix.org/python-dateutil"),
        make_option("--end", dest="end_time",
            help="consider entries no later than X"),
    ) + BaseCommand.option_list

    def handle(self, *args, **options):
        errors = 0
        regrades = 0
        updates = 0

        if len(args) != 1:
           raise CommandError("exam id is required")
        examid = args[0]

        start = parser.parse("1/1/1970")
        if 'start_time' in options and options['start_time']:
            start = parser.parse(options['start_time'])
        end = parser.parse("1/1/2038")  # almost the end of unix time
        if 'end_time' in options and options['end_time']:
            end = parser.parse(options['end_time'])

        exam_rec = Exam.objects.get(id__exact=examid)
        autograder = AutoGrader(exam_rec.xml_metadata)

        examRecords = ExamRecord.objects\
                .filter(exam_id__exact=examid, complete=True)\
                .filter(time_created__gt=start)\
                .filter(time_created__lt=end)
        if len(examRecords) == 0:
            print "warning: no exam records found, is that what you intended?"
            return

        count = 1
        for er in examRecords:
            print "ExamRecord %d, %d of %d" % (er.id, count, len(examRecords))
            count += 1
            try:
                score_before = er.score
                if score_before == None:     # scores of 0 come back from model as None
                    score_before = 0.0       # not sure why but they do
                score_after = 0.0
                submitted = json.loads(er.json_data)
                regrade = {}
                for prob, v in submitted.iteritems():
                    if isinstance(v,list):    # multiple choice case
                        student_input = map(lambda li: li['value'], v)
                        regrade[prob] = autograder.grade(prob, student_input)
                    else:                     # single answer case
                        student_input = v['value']
                        regrade[prob] = autograder.grade(prob, student_input)
                    if 'feedback' in regrade[prob]:
                        del regrade[prob]['feedback']   # remove giant feedback field
                    if 'score' in regrade[prob]:
                        score_after += float(regrade[prob]['score'])
                
                s = er.student
                status_line =  "%d, \"%s\", \"%s\", %s, %s, %s, %0.1f, %0.1f" \
                        % (er.id, s.first_name, s.last_name, s.username, s.email, 
                           str(er.time_created), score_before, score_after)
                if score_before == score_after:
                    print "OK: " + status_line
                    continue
                regrades += 1
                print "REGRADE: " + status_line
                if not options['dryrun']:
                    er.json_score_data = json.dumps(regrade)
                    er.score = score_after
                    er.save()
                    updates += 1

            # exception handler around big ExamRecords loop -- trust me, it lines up
            # this just counts and skips offending rows so we can keep making progress
            except Exception as e:
                print "ERROR: examrecord %d: cannot regrade: %s" % (er.id, str(e))
                errors += 1
                continue

        print
        print "## SUMMARY ##"
        print "# Errors: %d" % errors
        print "# Regrades: %d" % regrades
        print "# Database rows updated: %d" % updates


