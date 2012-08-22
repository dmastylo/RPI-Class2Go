from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
import re

from courses.actions import auth_view_wrapper

def index(item): # define a index function for list items
 return item[1]

def main(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    announcement_list = Announcement.objects.getByCourse(course=common_page_data['course'])
    if len(announcement_list) > 10:
        many_announcements = True
        announcement_list = announcement_list[0:10]
    else:
        many_announcements = False
    
    if request.user.is_authenticated():
        is_logged_in = 1
        news_list = common_page_data['production_course'].newsevent_set.all().order_by('-time_created')[0:5]
    else:
        is_logged_in = 0
        news_list = []

    contentsection_list = ContentSection.objects.getByCourse(course=common_page_data['course'])
    video_list = Video.objects.getByCourse(course=common_page_data['course'])
    pset_list =  ProblemSet.objects.getByCourse(course=common_page_data['course'])
    additional_pages =  AdditionalPage.objects.getSectionPagesByCourse(course=common_page_data['course'])

    full_index_list = []
    for contentsection in contentsection_list:
        index_list = []
        for video in video_list:
            if video.section.id == contentsection.id:
                index_list.append(('video', video.index, video.id, contentsection.id, video.slug, video.title))

        for pset in pset_list:
            if pset.section.id == contentsection.id:
                index_list.append(('pset', pset.index, pset.id, contentsection.id, pset.slug, pset.title))
                
        for page in additional_pages:
            if page.section.id == contentsection.id:
                index_list.append(('additional_page', page.index, page.id, contentsection.id, page.slug, page.title))

        index_list.sort(key = index)
        full_index_list.append(index_list)

    return render_to_response('courses/view.html',
            {'common_page_data': common_page_data,
             'announcement_list': announcement_list,
             'news_list': news_list,
             'contentsection_list': contentsection_list,
             'video_list': video_list,
             'pset_list': pset_list,
             'full_index_list': full_index_list,
             'is_logged_in': is_logged_in
             },

            context_instance=RequestContext(request))

@auth_view_wrapper
def course_materials(request, course_prefix, course_suffix):
    
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    section_structures = get_course_materials(common_page_data=common_page_data, get_video_content=True, get_pset_content=True, get_additional_page_content=True)
    
    return render_to_response('courses/'+common_page_data['course_mode']+'/course_materials.html', {'common_page_data': common_page_data, 'section_structures':section_structures, 'context':'course_materials'}, context_instance=RequestContext(request))

