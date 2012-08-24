from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from datetime import datetime
from models import Course
from courses.actions import is_member_of_course

### C2G Core Views ###

def home(request):
    now = datetime.now()
    courses = Course.objects.filter(calendar_start__gt=now, mode="production")
    available_course_list = []
    for course in courses:
        if is_member_of_course(course, request.user):
            course_student_member = 'True'
        else:
            course_student_member = 'False'
        
        viewable_handle = course.handle.replace('#$!', '/')
        available_course_list.append((course.title, course.handle, viewable_handle, course_student_member))
        
    return render_to_response('courses/signup.html', {'request': request, 'available_course_list': available_course_list}, context_instance=RequestContext(request))

def healthcheck(request):
    return HttpResponse("I'm alive!")

