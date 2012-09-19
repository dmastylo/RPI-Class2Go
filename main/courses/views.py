from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
import re
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from courses.forms import *

from courses.actions import auth_view_wrapper

from urlparse import urlparse

def index(item): # define a index function for list items
 return item[1]


curTerm = 'Fall2012'

def current_redirects(request, course_prefix):
    if Course.objects.filter(handle=course_prefix+'--'+curTerm).exists():
        return redirect(reverse('courses.views.main',args=[course_prefix, curTerm]))
    else: 
        raise Http404
    

def main(request, course_prefix, course_suffix):
    #Common page data is already run in middleware
    #try:
    #    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    #except Course.DoesNotExist:
    #    raise Http404

    common_page_data=request.common_page_data
    ##JASON 9/5/12###
    ##For Launch, but I don't think it needs to be removed later##
    if common_page_data['course'].preview_only_mode:
        if not common_page_data['is_course_admin']:
            return redirect(reverse('courses.preview.views.preview',args=[course_prefix, course_suffix]))

    
    announcement_list = Announcement.objects.getByCourse(course=common_page_data['course']).order_by('-time_created')[:11]
    if len(announcement_list) > 10:
        many_announcements = True
        announcement_list = announcement_list[0:10]
    else:
        many_announcements = False
    
    if request.user.is_authenticated():
        is_logged_in = 1
        news_list = common_page_data['ready_course'].newsevent_set.all().order_by('-time_created')[0:5]
    else:
        is_logged_in = 0
        news_list = []

    contentsection_list = ContentSection.objects.getByCourse(course=common_page_data['course'])
    video_list = Video.objects.getByCourse(course=common_page_data['course'])
    pset_list =  ProblemSet.objects.getByCourse(course=common_page_data['course'])
    additional_pages =  AdditionalPage.objects.getSectionPagesByCourse(course=common_page_data['course'])
    file_list = File.objects.getByCourse(course=common_page_data['course'])

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

        for file in file_list:
            if file.section.id == contentsection.id:
                file_path=urlparse(file.file.url).path
                file_parts=re.split('\.',file_path)
                file_extension=file_parts.pop().lower()
                if file_extension in ("html", "htm"):
                    icon_type="globe"
                elif (file_extension in ("ppt", "pptx")):
                    icon_type="list-alt"
                elif (file_extension in ('jpg', 'png', 'gif', 'jpeg')):
                    icon_type="picture"  
                elif (file_extension in ('mp3', 'aac')):
                    icon_type="music"
                else:
                    icon_type="file"
                index_list.append(('file', file.index, file.id, contentsection.id, file.file.url, file.title, icon_type))

        index_list.sort(key = index)
        full_index_list.append(index_list)


    return render_to_response('courses/view.html',
            {'common_page_data': common_page_data,
             'announcement_list': announcement_list,
             'many_announcements':many_announcements,
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


    section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True, get_pset_content=True, get_additional_page_content=True, get_file_content=True)

    form = None
    if request.common_page_data['course_mode'] == "draft":
        form = LiveDateForm()
    
    return render_to_response('courses/'+request.common_page_data['course_mode']+'/course_materials.html', {'common_page_data': request.common_page_data, 'section_structures':section_structures, 'context':'course_materials', 'form':form}, context_instance=RequestContext(request))

