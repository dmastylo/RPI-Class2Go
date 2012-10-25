# Create your views here.
import sys
import traceback
import json
import operator
import logging
logger = logging.getLogger(__name__)

from c2g.models import Exercise, Video, VideoToExercise, ProblemSet, ProblemSetToExercise, Exam, ExamRecord
from django.http import HttpResponse, HttpResponseBadRequest, Http404
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


@auth_view_wrapper
def view_my_submissions(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    subs = list(ExamRecord.objects.filter(course=course, exam=exam, student=request.user, time_created__lt=exam.grace_period).order_by('-time_created'))

    my_subs = map(lambda s: {'time_created':s.time_created, 'json_obj':sorted(json.loads(s.json_data).iteritems(), key=operator.itemgetter(0))}, subs)

    return render_to_response('exams/view_my_submissions.html', {'common_page_data':request.common_page_data, 'exam':exam, 'my_subs':my_subs},
                              RequestContext(request) )



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
    
    return HttpResponse("Entry has been saved")
