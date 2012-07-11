from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement, NewsEvent

def all(request):
	course_list = Course.objects.select_related('institution').all()
	return render_to_response('courses/all.html', {'request': request, 'course_list': course_list}, context_instance=RequestContext(request))
	
def current(request):
	return render_to_response('courses/current.html', {'request': request}, context_instance=RequestContext(request))
	
def mine(request):
	return render_to_response('courses/mine.html', {'request': request}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    announcement_list = course.announcement_set.all().order_by('-time_created')
    news_list = course.newsevent_set.all().order_by('-time_created')[0:5]
    return render_to_response('courses/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'announcement_list': announcement_list, 'news_list': news_list, 'request': request}, context_instance=RequestContext(request))

def info(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    return render_to_response('courses/info.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'request': request}, context_instance=RequestContext(request))
	
def syllabus(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    return render_to_response('courses/syllabus.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'request': request}, context_instance=RequestContext(request))

def prereqs(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    return render_to_response('courses/prereqs.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'request': request}, context_instance=RequestContext(request))
