from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement, NewsEvent
from courses.common_page_data import get_common_page_data
import re

def index(item): # define a index function for list items
 return item[1]

def main(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    announcement_list = common_page_data['course'].announcement_set.all().order_by('-time_created')
    news_list = common_page_data['course'].newsevent_set.all().order_by('-time_created')[0:5]
    contentsection_list = common_page_data['course'].contentsection_set.all().order_by('index')
    video_list = common_page_data['course'].video_set.all().order_by('index')
    pset_list =  common_page_data['course'].problemset_set.all().order_by('index')
    
    full_index_list = []
    for contentsection in contentsection_list:
        index_list = []
        for video in video_list:
            if video.section.id == contentsection.id:
                index_list.append(('video', video.index, video.id, contentsection.id, video.slug, video.title))
            
        for pset in pset_list:
            if pset.section.id == contentsection.id:
                index_list.append(('pset', pset.index, pset.id, contentsection.id, pset.title, pset.name))
                    
        index_list.sort(key = index)
        full_index_list.append(index_list)
    
    return render_to_response('courses/view.html', 
            {'common_page_data': common_page_data,
             'announcement_list': announcement_list, 
             'news_list': news_list,
             'contentsection_list': contentsection_list,
             'video_list': video_list,
             'pset_list': pset_list,
             'full_index_list': full_index_list
             }, 

            context_instance=RequestContext(request))

def overview(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

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
            context_instance=RequestContext(request))

def syllabus(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

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
            context_instance=RequestContext(request))
