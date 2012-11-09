# Create your views here.
import sys
import traceback
import json
import operator
import logging
import settings
import datetime
import HTMLParser

FILE_DIR = getattr(settings, 'FILE_UPLOAD_TEMP_DIR', '/tmp')
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
AWS_SECURE_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_SECURE_STORAGE_BUCKET_NAME', '')

logger = logging.getLogger(__name__)

from c2g.models import Exercise, Video, VideoToExercise, ProblemSet, ProblemSetToExercise, Exam, ExamRecord
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

    return render_to_response('exams/list.html',
                              {'common_page_data':request.common_page_data,
                               'course':course,
                              'exams':exams},
                              RequestContext(request))

# Create your views here.
@auth_view_wrapper
def show_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404
    
    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam}, RequestContext(request))

@require_POST
@auth_view_wrapper
def show_populated_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    parser = HTMLParser.HTMLParser()
    json_pre_pop = parser.unescape(request.POST['json-pre-pop'])
    editable = request.POST.get('latest', False)
 
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop, 'editable':editable}, RequestContext(request))

@auth_view_wrapper
def view_my_submissions(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    subs = list(ExamRecord.objects.filter(course=course, exam=exam, student=request.user, time_created__lt=exam.grace_period).order_by('-time_created'))

    my_subs = map(lambda s: {'time_created':s.time_created, 'json_obj':sorted(json.loads(s.json_data).iteritems(), key=operator.itemgetter(0)), 'plain_json_obj':json.dumps(json.loads(s.json_data)),'id':s.id}, subs)

    return render_to_response('exams/view_my_submissions.html', {'common_page_data':request.common_page_data, 'exam':exam, 'my_subs':my_subs},
                              RequestContext(request) )

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

    for s in submitters: #yes, there is sql in a loop here.  We'll optimize later
        latest_sub = ExamRecord.objects.values('student__username', 'time_created', 'json_data').filter(exam=exam, time_created__lt=exam.grace_period, student=s['student']).latest('time_created')
        for k,v in json.loads(latest_sub['json_data']).iteritems():
            str = '"%s","%s","%s"\n' % (latest_sub['student__username'], k, parse_val(v))
            outfile.write(str)

    outfile.write("\n")
    
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
    
    record = ExamRecord(course=course, exam=exam, student=request.user, json_data=request.POST['json_data'])
    record.save()
    
    return HttpResponse("Submission has been saved.")

def show_test_xml(request):
    return render_to_response('exams/test_xml.html', {'message':'what up G?'}, RequestContext(request))
