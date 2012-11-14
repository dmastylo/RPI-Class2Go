# Create your views here.
import sys
import traceback
import json
import operator
import logging
import settings
import datetime
import csv
import HTMLParser
from django.db.models import Sum

FILE_DIR = getattr(settings, 'FILE_UPLOAD_TEMP_DIR', '/tmp')
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
AWS_SECURE_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_SECURE_STORAGE_BUCKET_NAME', '')

logger = logging.getLogger(__name__)

from c2g.models import Exercise, Video, VideoToExercise, ProblemSet, ProblemSetToExercise, Exam, ExamRecord, ExamScore, ExamScoreField
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from django.core.exceptions import MultipleObjectsReturned
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse

from django.views.decorators.csrf import csrf_protect
from storages.backends.s3boto import S3BotoStorage


@auth_view_wrapper
def listAll(request, course_prefix, course_suffix):
    
    course = request.common_page_data['course']
    exams = list(Exam.objects.filter(course=course, is_deleted=0))

    if course.mode=="live":
        exams = filter(lambda item: item.is_live(), exams)
    
    scores = []

    for e in exams:
        if ExamScore.objects.filter(course=course, exam=e, student=request.user).exists():
            scores.append(ExamScore.objects.filter(course=course, exam=e, student=request.user)[0].score)
        else:
            scores.append(None)

    return render_to_response('exams/list.html',
                              {'common_page_data':request.common_page_data,
                               'course':course,
                              'exams_and_scores':zip(exams,scores)},
                              RequestContext(request))

# Create your views here.
@auth_view_wrapper
def show_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404
    
    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'json_pre_pop':"{}",
                              'scores':"{}",'editable':True,
                              'exam':exam}, RequestContext(request))

@require_POST
@auth_view_wrapper
def show_populated_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    parser = HTMLParser.HTMLParser()
    json_pre_pop = parser.unescape(request.POST['json-pre-pop'])
    scores = request.POST.get('scores',"{}")
    editable = request.POST.get('latest', False)
 
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop, 'scores':scores, 'editable':editable}, RequestContext(request))


@auth_view_wrapper
def show_graded_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    try:
        record = ExamRecord.objects.filter(course=course, exam=exam, student=request.user, time_created__lt=exam.grace_period).latest('time_created')
        json_pre_pop = record.json_data
    except ExamRecord.DoesNotExist:
        record = None
        json_pre_pop = "{}"

    try:
        score_obj = ExamScore.objects.get(course=course, exam=exam, student=request.user)
        score = score_obj.score
        score_fields = {}
        for s in list(ExamScoreField.objects.filter(parent=score_obj)):
            score_fields[s.field_name] = s.subscore
        scores_json = json.dumps(score_fields)
    except ExamScore.DoesNotExist, ExamScore.MultipleObjectsReturned:
        score = None
        score_fields = {}
        scores_json = "{}"

    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop, 'scores':scores_json, 'editable':False, 'score':score}, RequestContext(request))



@auth_view_wrapper
def view_my_submissions(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    subs = list(ExamRecord.objects.filter(course=course, exam=exam, student=request.user, time_created__lt=exam.grace_period).order_by('-time_created'))

    my_subs = map(lambda s: my_subs_helper(s), subs)

    try:
        score_obj = ExamScore.objects.get(course=course, exam=exam, student=request.user)
        score = score_obj.score
        score_fields = {}
        for s in list(ExamScoreField.objects.filter(parent=score_obj)):
            score_fields[s.field_name] = s.subscore

    except ExamScore.DoesNotExist, ExamScore.MultipleObjectsReturned:
        score = None
        score_fields = {}

    return render_to_response('exams/view_my_submissions.html', {'common_page_data':request.common_page_data, 'exam':exam, 'my_subs':my_subs,
                              'score_fields':json.dumps(score_fields), 'score':score}, RequestContext(request) )


def my_subs_helper(s):
    """Helper function to handle badly formed JSON stored in the database"""
    try:
        return {'time_created':s.time_created, 'json_obj':sorted(json.loads(s.json_data).iteritems(), key=operator.itemgetter(0)), 'plain_json_obj':json.dumps(json.loads(s.json_data)),'id':s.id}
    except ValueError:
        return {'time_created':s.time_created, 'json_obj':"__ERROR__", 'plain_json_obj':"__ERROR__", 'id':s.id}

@auth_is_course_admin_view_wrapper
def view_submissions_to_grade(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    if exam.mode=="draft":
        exam = exam.image

    submitters = ExamRecord.objects.filter(exam=exam,  time_created__lt=exam.grace_period).values('student').distinct()
    fname = course_prefix+"-"+course_suffix+"-"+exam_slug+"-"+datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+".csv"
    outfile = open(FILE_DIR+"/"+fname,"w+")

    could_not_parse = ""

    for s in submitters: #yes, there is sql in a loop here.  We'll optimize later
        latest_sub = ExamRecord.objects.values('student__username', 'time_created', 'json_data').filter(exam=exam, time_created__lt=exam.grace_period, student=s['student']).latest('time_created')
        try:
            sub_obj = json.loads(latest_sub['json_data']).iteritems()
            for k,v in sub_obj:
                outstring = '"%s","%s","%s"\n' % (latest_sub['student__username'], k, parse_val(v))
                outfile.write(outstring)
        except ValueError:
            could_not_parse += latest_sub['student__username']+ " " #Don't output if the latest submission was erroneous

    outfile.write("\n")

    #if there were items we could not parse
    if could_not_parse:
        #write the usernames at the beginning of the file
        outfile.seek(0)
        data=outfile.read()
        outfile.seek(0)
        outfile.truncate()
        outfile.write("Could not parse data from the following users: " + could_not_parse + "\n")
        outfile.write(data)

    #write to S3
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    s3file = secure_file_storage.open("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname),'w')
    outfile.seek(0)
    s3file.write(outfile.read())
    s3file.close()
    outfile.close()
    return HttpResponseRedirect(secure_file_storage.url("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname), response_headers={'response-content-disposition': 'attachment'}))

def parse_val(v):
    """Helper function to parse AJAX submissions"""
    if isinstance(v,list):
        sorted_list = sorted(map(lambda li: li['value'], v))
        return reduce(lambda x,y: x+y+",", sorted_list, "")
    elif isinstance(v,basestring):
        return v
    return str(v)


@require_POST
@auth_view_wrapper
def collect_data(request, course_prefix, course_suffix, exam_slug):
    
    course = request.common_page_data['course']
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    postdata = request.POST['json_data'] #will return an error code to the user if either of these fail (throws 500)
    json.loads(postdata)
    
    record = ExamRecord(course=course, exam=exam, student=request.user, json_data=request.POST['json_data'])
    record.save()
    
    return HttpResponse("Submission has been saved.")



@auth_is_course_admin_view_wrapper
def view_csv_grades(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    if course.mode=="draft":
        course = course.image

    if exam.mode=="draft":
        exam = exam.image
    
    graded_students = ExamScore.objects.filter(course=course, exam=exam).values('student','student__username').distinct()
    fname = course_prefix+"-"+course_suffix+"-"+exam_slug+"-grades-"+datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+".csv"
    outfile = open(FILE_DIR+"/"+fname,"w+")

    could_not_parse = ""

    for s in graded_students: #yes, there is sql in a loop here.  We'll optimize later
        #print(s)
        score_obj = ExamScore.objects.get(course=course, exam=exam, student=s['student'])
        subscores = ExamScoreField.objects.filter(parent=score_obj)
        for field in subscores:
            outstring = '"%s","%s","%s"\n' % (s['student__username'], field.field_name, str(field.subscore))
            outfile.write(outstring)

    outfile.write("\n")

    #write to S3
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    s3file = secure_file_storage.open("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname),'w')
    outfile.seek(0)
    s3file.write(outfile.read())
    s3file.close()
    outfile.close()
    return HttpResponseRedirect(secure_file_storage.url("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname), response_headers={'response-content-disposition': 'attachment'}))




@require_POST
@auth_view_wrapper
def post_csv_grades(request, course_prefix, course_suffix, exam_slug):
    
    course = request.common_page_data['course']
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    #Only process ready mode exams and courses

    if course.mode == "draft":
        course = course.image
            
    if exam.mode == "draft":
        exam = exam.image

        
    good_count = 0
    exam_scores = {} #this will be the student score created
    bad_rows = []

    db_hits = 0

    if request.FILES:
        row_count=0;
        #We build up the records to be saved as a dict
        for f in request.FILES.itervalues():
            reader = csv.reader(f)
            for row in reader:  # each row should be: "<student_username>", "<field_name>", "subscore"
                row_count += 1
                valid, output = validate_row(row)
                if not valid:
                    bad_rows.append(str(row_count) + ":" + str(row) + " => " + output)
                    logger.error(str(row_count) + ":" + str(row) + " => " + output)
                else:
                    (username, field_name, score) = output
                    
                    if username in exam_scores:
                        exam_scores[username]['fields'].append({'name':field_name, 'score':score})
                        exam_scores[username]['total'] += score #increment total score
                    else:
                        exam_scores[username]={'fields':[{'name':field_name, 'score':score}], 'total':score} #initialize
                    
                    good_count += 1

                    if good_count % 100 == 0:
                        print str(good_count)

    student_count = 0
    for username, record in exam_scores.iteritems():
        try:
            user = User.objects.get(username=username)
            user_score, created = ExamScore.objects.get_or_create(course=course, exam=exam, student=user)
            db_hits += 2
            
            if not created:
                #yes, we delete them all to start.  Uploading a CSV replaces the grades for this student on this exam
                #we do this to allow batched SQL later
                ExamScoreField.objects.filter(parent=user_score).delete()
                db_hits += 1
            
            field_objs = map(lambda f:ExamScoreField(parent=user_score, field_name=f['name'], subscore=f['score']), record['fields'])
            ExamScoreField.objects.bulk_create(field_objs)
            db_hits += 1

            total_1 = sum(map(lambda r:r['score'], record['fields']))
            if total_1 != record['total']:
                bad_rows.append(username + ": total does not match sum of subscores.  Sum:" + str(total_1) + " Total:" + str(record['total']))
                logger.error(username + ": total does not match sum of subscores.  Sum:" + str(total_1) + " Total:" + str(record['total']))
            user_score.score = max(record['total'],0) #0 is the floor score
            user_score.save()
            db_hits += 1
        
            student_count += 1

            if student_count % 100 == 0:
                print str(student_count)
        
        except User.DoesNotExist:
            bad_rows.append(username + " not found in students list!")
            logger.error(username + " not found in students list!")

    logger.info("Good count: %d  Student count: %d  DB Hits: %d  Bad rows:%s" % (good_count, student_count, db_hits, str(bad_rows)))

    return render_to_response('exams/csv_upload_confirm.html',
                              {'common_page_data':request.common_page_data,
                               'exam':exam,
                               'good_count':good_count,
                               'db_hits':db_hits,
                               'student_count':student_count,
                               'bad_rows':bad_rows},
                              RequestContext(request))



def validate_row(row):
    """
        Helper function to validate a row read in from CSV.
        If validation fails, returns tuple of (False, error message).
        If validation succeeds, returns tuple of (True, (username, field_name, score))
    """

    if not isinstance(row, list):
        return (False, "Badly formatted row")

    if len(row) != 3:
        return  (False, "Too few or too many items in row (should be 3)")

    [username, field_name, score_str] = row
        
    if not isinstance(username, str):
        return (False, "Username is not a string")
            
    if not username:
        return (False, "Username is empty string")

    if not isinstance(field_name, str):
        return (False, "Field name is not a string")

    if not field_name:
        return (False, "Field name is empty string")

    try:
        score = int(score_str)
        if score > 10000 or score < -10000:
            return (False, "The score must be between -10000 and 10000")
    except ValueError:
        return (False, "Score cannot be converted to integer")

    return (True, (username, field_name, score))