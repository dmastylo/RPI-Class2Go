from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from datetime import datetime
from models import Course
from courses.actions import is_member_of_course
from courses.actions import auth_view_wrapper

### C2G Core Views ###

@auth_view_wrapper
def home(request):
    #try:
    #    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    #except:
    raise Http404
    
    
    now = datetime.now()
    courses = Course.objects.filter(calendar_start__gt=now, mode="production")
    available_course_list = []
    for course in courses:
        if is_member_of_course(course, request.user):
            course_student_member = 'True'
        else:
            course_student_member = 'False'
        
        viewable_handle = course.handle.replace('--', '/')
        available_course_list.append((course.title, course.handle, viewable_handle, course_student_member))
        
    return render_to_response('courses/signup.html', {'request': request, 'available_course_list': available_course_list}, context_instance=RequestContext(request))

def healthcheck(request):
    return HttpResponse("I'm alive!")

def throw500(request):
    raise BaseException('Testing the exception--http500 mechanism')

def throw404(request):
    raise Http404

def hc(request):
    return render_to_response('honor_code.html',{},RequestContext(request))

def tos(request):
    return render_to_response('TOS.html',{},RequestContext(request))

def privacy(request):
    return render_to_response('privacy.html',{},RequestContext(request))

def contactus(request):
    return render_to_response('contactus.html',{},RequestContext(request))