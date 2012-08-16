from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from datetime import datetime
from models import Course


### C2G Core Views ###

def home(request):
    now = datetime.now()
    courses = Course.objects.filter(calendar_start__gt=now, mode="production")
    available_course_list = []
    for course in courses:
        handle = course.handle.replace('#$!', '/')
        available_course_list.append((course.title, handle))
        
    return render_to_response('base.html', {'request': request, 'available_course_list': available_course_list}, context_instance=RequestContext(request))

def healthcheck(request):
    return HttpResponse("I'm alive!")

