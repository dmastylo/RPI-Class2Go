from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest.serializers import *

from django.http import HttpResponse, Http404
from registration.backends import get_backend
from django.template import RequestContext
from django.core.urlresolvers import reverse
from courses.common_page_data import get_common_page_data
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import login
from django.views.decorators.cache import never_cache
from django.contrib.auth import login as auth_login
from django.conf import settings
from c2g.util import upgrade_to_https_and_downgrade_upon_redirect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils import simplejson
from c2g.models import *
from django.contrib import auth

import json
import settings
import os.path

import logging
logger=logging.getLogger("foo")


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders it's content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@sensitive_post_parameters()
@never_cache
@require_POST
@csrf_protect
#@upgrade_to_https_and_downgrade_upon_redirect
def rest_login(request):
    """
    Login to c2g if ok return course list student registered for
    """
    login_form = AuthenticationForm(data=request.POST)

    if login_form.is_valid():
  
        auth_login(request, login_form.get_user())
        course_list = Course.objects.all()
        groups = request.user.groups.all()
        courses = []
        for g in groups:
            for c in course_list:
                if (g.id == c.student_group_id or g.id == c.instructor_group_id or g.id == c.tas_group_id or g.id == c.readonly_tas_group_id) and c.mode != 'draft':
                    courses.append({'course_id':c.id})
                    break
        
        
        to_json = {'userid': request.user.username, 'email': request.user.email, 'last_name':request.user.last_name,
                   'first_name':request.user.first_name,'date_joined':request.user.date_joined.strftime('%Y-%m-%dT%H:%M:%S'),
                   'last_login': request.user.last_login.strftime('%Y-%m-%dT%H:%M:%S'),'courses':courses}
    else:
        to_json = {"login": "error"}



    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


"""
Gets Problemset Activities for student
"""

class ProblemActivities(APIView):

    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
        
    def get(self, request):

        problem_activities = ProblemActivity.objects.filter(student=request.user)
                
        index_list = []
        for prob in problem_activities:
            index_list.append({'id': prob.id, 'video_to_exercise': prob.video_to_exercise_id, 
                               'problemset_to_exercise': prob.problemset_to_exercise_id,
                               'problem_identifier': prob.problem_identifier, 'complete': prob.complete, 'attempt_content': prob.attempt_content,
                               'count_hints':prob.count_hints, 'time_taken':prob.time_taken,'attempt_number': prob.attempt_number,
                               'sha1':prob.sha1, 'seed': prob.seed,'problem_type':prob.problem_type,'review_mode':prob.review_mode,
                               'topic_mode':prob.topic_mode,'casing':prob.casing,'card':prob.card,'cards_done':prob.cards_done,
                               'cards_left':prob.cards_left,'user_selection_val':prob.user_selection_val,'user_choices':prob.user_choices})

        
        return Response(index_list)

        
class VideoActivities(APIView):

    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)   
    
    def get(self, request):

        video_activities = VideoActivity.objects.filter(student=request.user)
                
        index_list = []
        for vid_activity in video_activities:
            index_list.append({'id': vid_activity.id, 'course': vid_activity.course_id, 
                               'video': vid_activity.video_id,
                               'start_seconds': vid_activity.start_seconds})

        
        
        return Response(index_list)

class FilesList(APIView):

    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)    
    def get(self, request):
        files = File.objects.all()
        serializer = FileSerializer(files)
    
        return Response(serializer.data)

class CourseList(APIView):
    
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        courses= Course.objects.all()
        serializer = CourseSerializer(courses)
    
        return Response(serializer.data)

	
class AnnouncementList(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        announcements= Announcement.objects.all()
        serializer = AnnouncementSerializer(announcements)
    
        return Response(serializer.data)
    

class ProblemSetList(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        psets = ProblemSet.objects.all()
        serializer = PSetSerializer(psets)
    
        return Response(serializer.data)
    
    
class ProblemSetToExerciseList(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        psetexes = ProblemSetToExercise.objects.all()
        serializer = PSetExerciseSerializer(psetexes)
    
        return Response(serializer.data)
    

class ExerciseList(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        exercises= Exercise.objects.all()
        serializer = ExerciseSerializer(exercises)
    
        return Response(serializer.data)
        

    

class ContentSectionList(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        content_sections = ContentSection.objects.all()
        serializer = ContentSectionSerializer(content_sections)
    
        return Response(serializer.data)
    


class VideoList(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos)
    
        return Response(serializer.data)
    
    
class VideoToExerciseList(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        vidtoexes = VideoToExercise.objects.all()
        serializer = VideoToExerciseSerializer(vidtoexes)
    
        return Response(serializer.data)

"""
Gets ExamScores for student
"""

class ExamRecordList(APIView):

    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
        
    def get(self, request):

        exam_records = ExamRecord.objects.filter(student=request.user)
                
        serializer = ExamRecordSerializer(exam_records)
    
        return Response(serializer.data)

class ExamScoreList(APIView):

    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
        
    def get(self, request):

        exam_scores = ExamScore.objects.filter(student=request.user)
                
        serializer = ExamScoreSerializer(exam_scores)
    
        return Response(serializer.data)

class ExamScoreFieldList(APIView):

    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
        
    def get(self, request):

        exam_score_fields = ExamScoreField.objects.filter(student=request.user)
                
        serializer = ExamScoreFieldSerializer(exam_score_fields)
    
        return Response(serializer.data)

class ExamList(APIView):

    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
        
    def get(self, request):

        course_id = request.GET.get('course')
        exams = Exam.objects.filter()
                
        serializer = ExamSerializer(exams)
    
        return Response(serializer.data)
