from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement, NewsEvent

def main(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    announcement_list = course.announcement_set.all().order_by('-time_created')
    news_list = course.newsevent_set.all().order_by('-time_created')[0:5]
    return render_to_response('courses/view.html',
            {'request': request,
             'course_prefix': course_prefix,
             'course_suffix': course_suffix,
             'course': course,
             'announcement_list': announcement_list,
             'news_list': news_list,
             },
            context_instance=RequestContext(request))

def overview(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    return render_to_response('courses/overview.html',
            {'request': request,
             'course_prefix': course_prefix,
             'course_suffix': course_suffix,
             'course': course,
             },
            context_instance=RequestContext(request))

def syllabus(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    return render_to_response('courses/syllabus.html',
            {'request': request,
             'course_prefix': course_prefix,
             'course_suffix': course_suffix,
             'course': course,
             },
            context_instance=RequestContext(request))
