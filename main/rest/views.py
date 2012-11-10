from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import ListOrCreateModelView
from djangorestframework.compat import View
from djangorestframework.response import Response
from djangorestframework import status
from djangorestframework.mixins import ResponseMixin
from djangorestframework.renderers import JSONRenderer
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
from courses.common_page_data import get_common_page_data
from c2g.models import *
from django.contrib import auth

import json
import settings
import os.path

import logging
logger=logging.getLogger("foo")


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
        
     
        #print request.user.email

        
        to_json = {'userid': request.user.username, 'email': request.user.email, 'last_name':request.user.last_name,
                   'first_name':request.user.first_name,'date_joined':request.user.date_joined.strftime('%Y-%m-%dT%H:%M:%S'),
                   'last_login': request.user.last_login.strftime('%Y-%m-%dT%H:%M:%S'),'courses':courses}
    else:
        to_json = {"login": "error"}



    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


"""
Gets Problemset Activities for student
"""

class ProblemsetActivities(ResponseMixin, View):

    renderers = (JSONRenderer,)
    def get(self, request):

        problem_activities = ProblemActivity.objects.filter(student=request.user)
                
        index_list = []
        for prob in problem_activities:
            index_list.append({'id': prob.id, 'video_to_exercise_id': prob.video_to_exercise_id, 
                               'problemset_to_exercise_id': prob.problemset_to_exercise_id,
                               'problem_identifier': prob.problem_identifier, 'complete': prob.complete, 'attempt_content': prob.attempt_content,
                               'count_hints':prob.count_hints, 'time_taken':prob.time_taken,'attempt_number': prob.attempt_number,
                               'sha1':prob.sha1, 'seed': prob.seed,'problem_type':prob.problem_type,'review_mode':prob.review_mode,
                               'topic_mode':prob.topic_mode,'casing':prob.casing,'card':prob.card,'cards_done':prob.cards_done,
                               'cards_left':prob.cards_left,'user_selection_val':prob.user_selection_val,'user_choices':prob.user_choices})

        response = Response(200, index_list)
        
        return self.render(response)

        
class VideoActivities(ResponseMixin, View):

    renderers = (JSONRenderer,)
    
    def get(self, request):

        video_activities = VideoActivity.objects.filter(student=request.user)
                
        index_list = []
        for vid_activity in video_activities:
            index_list.append({'id': vid_activity.id, 'course_id': vid_activity.course_id, 
                               'video_id': vid_activity.video_id,
                               'start_seconds': vid_activity.start_seconds})

        response = Response(200, index_list)
        
        return self.render(response)

class Files(ResponseMixin, View):

    renderers = (JSONRenderer,)
    
    def get(self, request):

        course = request.common_page_data['course']
        files = Files.objects.filter(course=course,is_deleted=0)
                
        index_list = []
        for aFile in files:
            index_list.append({'id': file.id, 'course_id': file.course_id, 
                               'is_deleted': file.is_deleted,
                               'index': file.index, 'section_id':file.section_id,'title':file.title,'file':file.file,
                               'mode':file.mode,'handle':file.handle})

        response = Response(200, index_list)
        
        return self.render(response)


class AuthenticatedListOrCreateModelView(ListOrCreateModelView):
	permissions = (IsAuthenticated, )


