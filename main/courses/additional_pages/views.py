from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from c2g.models import *
from courses.common_page_data import get_common_page_data
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper
from courses.views import get_full_contentsection_list


@auth_is_course_admin_view_wrapper
def manage_nav_menu(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', course_prefix, course_suffix)
    
    return render_to_response('additional_pages/manage_nav_menu.html', {'common_page_data':common_page_data, 'mode':'nav_menu'}, context_instance=RequestContext(request))

@auth_is_course_admin_view_wrapper
def add_section_page(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', course_prefix, course_suffix)
    
    sections = ContentSection.objects.getByCourse(course=common_page_data['course'])
    return render_to_response('additional_pages/add_section_page.html', {'common_page_data':common_page_data, 'mode':'section', 'sections':sections}, context_instance=RequestContext(request))

@auth_view_wrapper
def main(request, course_prefix, course_suffix, slug):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
        page = AdditionalPage.objects.get(course=common_page_data['course'], slug=slug)
    except:
        raise Http404
    
    if not common_page_data['is_course_admin']:
        visit_log = PageVisitLog(
            course = common_page_data['ready_course'],
            user = request.user,
            page_type = 'additional_page',
            object_id = str(page.id),
        )
        visit_log.save()
        
    if common_page_data['is_course_admin'] and common_page_data['course_mode'] == 'draft' and common_page_data['view_mode'] == 'edit':
        template = 'additional_pages/edit.html'
    else:
        template = 'additional_pages/view.html'
        
    course = common_page_data['course']
    full_contentsection_list, full_index_list = get_full_contentsection_list(course)

    if request.user.is_authenticated():
        is_logged_in = 1
    else:
        is_logged_in = 0

    return render_to_response(template,
                              {'common_page_data': common_page_data,
                               'page': page,
                               'contentsection_list': full_contentsection_list, 
                               'full_index_list': full_index_list,
                               'is_logged_in': is_logged_in},
                               context_instance=RequestContext(request))
