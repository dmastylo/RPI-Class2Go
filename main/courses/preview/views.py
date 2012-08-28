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

import json
import settings

backend = get_backend('registration.backends.simple.SimpleBackend')
form_class = RegistrationFormUniqueEmail


def preview(request, course_prefix, course_suffix):
    """
    Much code borrowed from registration.views.register
    """
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    
    form = form_class(initial={'course_prefix':course_prefix,'course_suffix':course_suffix})
    context = RequestContext(request)
    return render_to_response('courses/preview.html',
                              {'form': form,'common_page_data': request.common_page_data},
                              context_instance=context)

@require_POST
@csrf_protect
def preview_reg(request, course_prefix, course_suffix):
    """
    Registering for a course in preview mode
    """
    form = form_class(data=request.POST, files=request.FILES)
    if form.is_valid():
        new_user = backend.register(request, **form.cleaned_data)
        course_group = request.common_page_data['course'].student_group
        course_group.user_set.add(new_user)
        if date.today() > request.common_page_data['course'].calendar_start :
            redirect_to = 'courses.views.main'
        else:
            redirect_to = 'courses.preview.views.preview'
        return redirect(reverse(redirect_to, args=[course_prefix, course_suffix]))
    else:
        context = RequestContext(request)                
        return render_to_response('courses/preview.html',
                          {'form': form,'common_page_data': request.common_page_data},
                          context_instance=context)
        