from django.contrib import messages
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from c2g.models import *
from courses.actions import auth_is_course_admin_view_wrapper
from courses.common_page_data import get_common_page_data
from courses.content_sections.forms import *
from courses.copy_content import copySection


@auth_is_course_admin_view_wrapper
def reorder(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main',  course_prefix, course_suffix)
        
    sections = ContentSection.objects.getByCourse(course=common_page_data['course'])
    
    return render_to_response('content_sections/draft/reorder.html', {'common_page_data': common_page_data, 'sections':sections}, context_instance=RequestContext(request))

@auth_is_course_admin_view_wrapper
def rename(request, course_prefix, course_suffix, section_id):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main',  course_prefix, course_suffix)
        
    section = ContentSection.objects.get(id=section_id)
    return render_to_response('content_sections/draft/rename.html', {'common_page_data': common_page_data, 'section':section}, context_instance=RequestContext(request))



@auth_is_course_admin_view_wrapper
def copy_content_form(request, course_prefix, course_suffix):
    draft_course = request.common_page_data['draft_course']
    share_iter = draft_course.share_to.all()
    share_list = map(lambda c: (c if c.mode=='draft' else c.image), list(share_iter)) # Make sure we get the draft version
    draft_sections = ContentSection.objects.filter(is_deleted=False, course=draft_course)
    #create a dynamic form class just for display
    form = SectionPushForm(list(draft_sections),share_list)
    
    return render_to_response('content_sections/push_content_form.html',
                              {'common_page_data':request.common_page_data, 'sections':draft_sections, 'form':form},
                              context_instance=RequestContext(request))

@auth_is_course_admin_view_wrapper
@require_POST
@csrf_protect
def copy_content(request, course_prefix, course_suffix):
    try:
        to_course = Course.objects.get(handle=request.POST['linked_class'], mode='draft')
        from_section = ContentSection.objects.get(id=request.POST['section_choice'])
        from_section = from_section if from_section.mode=="draft" else from_section.image #make sure we have a draft mode section
    except Course.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'The destination course does not exist.')
        return redirect('courses.content_sections.views.copy_content_form', course_prefix, course_suffix)
    except ContentSection.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'The selected content section does not exist.')
        return redirect('courses.content_sections.views.copy_content_form', course_prefix, course_suffix)

    if not request.user in list(to_course.get_all_course_admins()):
        messages.add_message(request, messages.ERROR, 'Sorry, you are not a staff member of the destination course.  Please contact support staff to request that privilege.')
        return redirect('courses.content_sections.views.copy_content_form', course_prefix, course_suffix)

    #privileges are okay, do the copy

    copySection(from_section, to_course)

    messages.add_message(request, messages.SUCCESS, 'Section: %s has been successfully copied to course: %s' %(from_section.title, to_course.title))

    return redirect('courses.views.main', course_prefix, course_suffix)

