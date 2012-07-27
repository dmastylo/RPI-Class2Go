from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement, NewsEvent
from courses.common_page_data import get_common_page_data
import re

def main(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
<<<<<<< HEAD
        
    announcement_list = common_page_data['course'].announcement_set.all().order_by('-time_created')
    news_list = common_page_data['course'].newsevent_set.all().order_by('-time_created')[0:5]
    return render_to_response('courses/view.html', 
            {'common_page_data': common_page_data,
             'announcement_list': announcement_list, 
             'news_list': news_list, 
             }, 
=======
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
>>>>>>> 718741d3c4d9a71e19c4579a2cc1f30c927fea0f
            context_instance=RequestContext(request))

def overview(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
<<<<<<< HEAD

    if request.method == 'POST':
        if request.POST.get("revert") == '1':
            common_page_data['staging_course'].description = common_page_data['production_course'].description
            common_page_data['staging_course'].save()
        else:
            common_page_data['staging_course'].description = request.POST.get("description")
            common_page_data['staging_course'].save()
            if request.POST.get("commit") == '1':
                common_page_data['production_course'].description = common_page_data['staging_course'].description
                common_page_data['production_course'].save()
        
    return render_to_response('courses/overview.html', 
            {'common_page_data': common_page_data}, 
=======
    return render_to_response('courses/overview.html',
            {'request': request,
             'course_prefix': course_prefix,
             'course_suffix': course_suffix,
             'course': course,
             },
>>>>>>> 718741d3c4d9a71e19c4579a2cc1f30c927fea0f
            context_instance=RequestContext(request))

def syllabus(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
<<<<<<< HEAD

    if request.method == 'POST':
        if request.POST.get("revert") == '1':
            common_page_data['staging_course'].syllabus = common_page_data['production_course'].syllabus
            common_page_data['staging_course'].save()
        else:
            common_page_data['staging_course'].syllabus = request.POST.get("syllabus")
            common_page_data['staging_course'].save()
            if request.POST.get("commit") == '1':
                common_page_data['production_course'].syllabus = common_page_data['staging_course'].syllabus
                common_page_data['production_course'].save()
        
    return render_to_response('courses/syllabus.html', 
            {'common_page_data': common_page_data}, 
=======
    return render_to_response('courses/syllabus.html',
            {'request': request,
             'course_prefix': course_prefix,
             'course_suffix': course_suffix,
             'course': course,
             },
>>>>>>> 718741d3c4d9a71e19c4579a2cc1f30c927fea0f
            context_instance=RequestContext(request))
