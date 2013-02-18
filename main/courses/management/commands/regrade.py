#!/usr/bin/env python

from optparse import make_option
from dateutil import parser

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from c2g.models import ExamRecord, Exam, ExamScore, ExamRecordScore
from courses.exams.autograder import *
from courses.exams.views import compute_penalties

class Command(BaseCommand):
    args = "<exam id>"
    help = "Regrade all results for an exam and report scores that are incorrect. With the -u option update the database."

    option_list = (
        make_option("-u", "--update", action="store_false", dest="dryrun", default=True,
            help="update regraded rows in database (default is dry run)"),
        make_option("-s", "--student", dest="student_ids",
            help="comma-separated list of students, identified by ids"),
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

        exam_obj = Exam.objects.get(id__exact=examid) 
        autograder = AutoGrader(exam_obj.xml_metadata)

        examRecords = ExamRecord.objects \
                .select_related('examrecordscore', 'student') \
                .filter(exam_id__exact=examid, complete=True)
        if options['start_time']:
            start = parser.parse(options['start_time'])
            examRecords = examRecords.filter(time_created__gt=start)
        if options['end_time']:
            end = parser.parse(options['end_time'])
            examRecords = examRecords.filter(time_created__lt=end)
        if options['student_ids']:
            sidlist = string.split(options['student_ids'], ',')
            examRecords = examRecords.filter(student__in=sidlist)

        # this executes the query
        if len(examRecords) == 0:
            print "warning: no exam records found, is that what you intended?"
            return

        count = 1
        for er in examRecords:
            ers_created = False
            ers = er.examrecordscore
            if ers is None:
                ers = ExamRecordScore(record=er, raw_score=0.0)
                ers_created = True
            print "ExamRecord %d, %d of %d" % (er.id, count, len(examRecords))
            count += 1
            try:
                score_before = er.score
                rawscore_before = ers.raw_score
                if score_before == None:     # scores of 0 come back from model as None
                    score_before = 0.0       # not sure why but they do
                if rawscore_before == None:  # scores of 0 come back from model as None
                    rawscore_before = 0.0    # not sure why but they do
                score_after = 0.0
                rawscore_after = 0.0
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
                        rawscore_after += float(regrade[prob]['score'])
            
                is_late = er.time_created > exam_obj.grace_period
                if er.attempt_number == 0:
                    print "ERROR: examrecord %d: skip, attempt_number=0" % er.id
                    errors += 1
                    next
                score_after = compute_penalties(rawscore_after, er.attempt_number,
                                                exam_obj.resubmission_penalty,
                                                is_late, exam_obj.late_penalty)
                s = er.student

                try:
                    es = ExamScore.objects.get(exam=exam_obj, student=s)
                    examscore_before = es.score
                except ExamScore.DoesNotExist:
                    es = ExamScore(course=er.course, exam=exam_obj, student=s)
                    examscore_before = -1
                examscore_after = max(examscore_before, score_after)
                
                #raw = raw score, score = with penalties, agg = exam_score, over all attempts
                status_line =  "%d, \"%s\", \"%s\", %s, %s, %s, raw:%0.1f->%0.1f score:%0.1f->%0.1f agg:%0.1f->%0.1f late:%d->%d" \
                        % (er.id, s.first_name, s.last_name, s.username, s.email, 
                           str(er.time_created), rawscore_before, rawscore_after,
                           score_before, score_after, examscore_before, examscore_after,
                           er.late, is_late)
                        
                if score_before == score_after and rawscore_before == rawscore_after \
                   and examscore_before == examscore_after and is_late == er.late :
                    print "OK: " + status_line
                    continue

                regrades += 1
                print "REGRADE: " + status_line

                if not options['dryrun']:
                    if score_before != score_after or is_late != er.late:
                        er.json_score_data = json.dumps(regrade)
                        er.score = score_after
                        er.late = is_late
                        er.save()
                        updates += 1
                    if ers_created or rawscore_before != rawscore_after:
                        ers.raw_score = rawscore_after
                        ers.save()
                        updates += 1
                    if examscore_before != examscore_after:
                        es.score = examscore_after
                        es.save()
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


