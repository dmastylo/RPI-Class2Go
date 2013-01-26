# Create your views here.

from django.http import HttpResponse, Http404
from registration.forms import RegistrationFormUniqueEmail
from registration.backends import get_backend
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from registration.backends import get_backend
from courses.common_page_data import get_common_page_data
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from datetime import date
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import login
from django.views.decorators.cache import never_cache
from django.contrib.auth import login as auth_login
from django.conf import settings
from c2g.util import upgrade_to_https_and_downgrade_upon_redirect
from django.views.decorators.debug import sensitive_post_parameters
from c2g.models import Video, Instructor, CourseInstructor

import json
import settings
import os.path

import logging
logger=logging.getLogger("foo")

backend = get_backend('registration.backends.simple.SimpleBackend')
form_class = RegistrationFormUniqueEmail


@upgrade_to_https_and_downgrade_upon_redirect
def preview(request, course_prefix, course_suffix):
    """
    Much code borrowed from registration.views.register
    """
    if request.common_page_data['is_course_admin']:
        return redirect('http://'+request.get_host()+reverse('courses.views.main', args=[course_prefix, course_suffix]))
    
    if request.common_page_data['is_course_member'] and not request.common_page_data['course'].preview_only_mode and \
       date.today() >= request.common_page_data['course'].calendar_start :
        return redirect('http://'+request.get_host()+reverse('courses.views.main', args=[course_prefix, course_suffix]))

    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    
    try:
        video = Video.objects.getByCourse(course=request.common_page_data['course']).get(slug='intro')
    except Video.DoesNotExist:
        video = None
        
    course_instructors = CourseInstructor.objects.getByCourse(course=request.common_page_data['course'])
    instructors = []
    
    for ci in course_instructors:
        instructors.append(ci.instructor)
              
    form = form_class(initial={'course_prefix':course_prefix,'course_suffix':course_suffix})
    login_form = AuthenticationForm(request)
    context = RequestContext(request)

    # default template, unless there is one in the soruce tree, then use that
    template_name='previews/default.html'
    class_template='previews/'+request.common_page_data['course'].handle+'.html'
    if os.path.isfile(settings.TEMPLATE_DIRS+'/'+class_template):
        template_name=class_template

    return render_to_response(template_name,
                              {'form': form,
                               'login_form': login_form,
                               'video':video,
                               'instructors':instructors,
                               'common_page_data': request.common_page_data,
                               'course': request.common_page_data['course'],
                               'display_login': request.GET.__contains__('login')},
                               context_instance=context)

@sensitive_post_parameters()
@never_cache
@require_POST
@csrf_protect
@upgrade_to_https_and_downgrade_upon_redirect
def preview_login(request, course_prefix, course_suffix):
    """
    Login to c2g in preview mode
    """
    login_form = AuthenticationForm(data=request.POST)
    if login_form.is_valid():
        auth_login(request, login_form.get_user())
        if not request.common_page_data['course'].preview_only_mode and \
           date.today() >= request.common_page_data['course'].calendar_start :
            redirect_to = 'courses.views.main'
        else:
            redirect_to = 'courses.preview.views.preview'
        return redirect(reverse(redirect_to, args=[course_prefix, course_suffix]))
    else:
        form = form_class(initial={'course_prefix':course_prefix,'course_suffix':course_suffix})
        context = RequestContext(request)                
        return render_to_response(#'previews/'+request.common_page_data['course'].handle+'.html',
                                  'previews/default.html',
                                  {'form': form,
                                   'login_form': login_form,
                                   'common_page_data': request.common_page_data,
                                   'display_login': True},
                                  context_instance=context)

@sensitive_post_parameters()
@require_POST
@csrf_protect
@never_cache
@upgrade_to_https_and_downgrade_upon_redirect
def preview_reg(request, course_prefix, course_suffix):
    """
    Registering for a course in preview mode
    """
    form = form_class(data=request.POST, files=request.FILES)
    if form.is_valid():
        new_user = backend.register(request, **form.cleaned_data)
        course_group = request.common_page_data['course'].student_group
        course_group.user_set.add(new_user)
        if not request.common_page_data['course'].preview_only_mode and \
           date.today() >= request.common_page_data['course'].calendar_start :
            redirect_to = 'courses.views.main'
        else:
            redirect_to = 'courses.preview.views.preview'
        return redirect(reverse(redirect_to, args=[course_prefix, course_suffix]))
    else:
        login_form = AuthenticationForm(data=request.POST)
        context = RequestContext(request)                
        return render_to_response(#'previews/'+request.common_page_data['course'].handle+'.html',
                                  'previews/default.html',
                                      {'form': form,
                                      'login_form': login_form,
                                      'common_page_data': request.common_page_data,
                                      'display_login': False},
                                      context_instance=context)
