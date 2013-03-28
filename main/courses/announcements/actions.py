from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from c2g.models import *
from courses.common_page_data import get_common_page_data
from courses.actions import always_switch_mode, auth_is_course_admin_view_wrapper
from django.views.decorators.http import require_POST

@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode     # Not strictly necessary but good for consistency
def add_announcement(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
        
    index = len(Announcement.objects.getByCourse(course=common_page_data['course']))
    announcement = Announcement(
        course=common_page_data['course'],
        title=request.POST.get("title"),
        description=request.POST.get("description"),
        index=index,
        mode='draft',
        owner=request.user,
    )
    announcement.save()
    
    announcement.create_ready_instance()
    
    if request.POST.get("commit") == '1':
        announcement.commit()

    if request.POST.get("email"):
        request.session['email_subject'] = announcement.title
        request.session['email_message'] = announcement.description
        messages.add_message(request, messages.SUCCESS, 'Your announcement is published! Now send it to the students.')
        return redirect('courses.email_members.views.email_members', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    
    return redirect(request.META['HTTP_REFERER'])
    
@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode     # Not strictly necessary but good for consistency
def save_announcement(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
        
    announcement = Announcement.objects.get(id=request.POST.get("announcement_id"))
    announcement.title = request.POST.get("title")
    announcement.description = request.POST.get("description")
    announcement.save()
    
    if request.POST.get("commit") == '1':
        announcement.commit()
        
    if request.POST.get("revert") == '1':
        announcement.revert()

    return redirect('courses.announcements.views.list', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    
@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode
def delete_announcement(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))

    announcement = Announcement.objects.get(id=request.POST.get("announcement_id"))
    announcement.delete()
    
    if announcement.image:
        announcement.image.delete()
    
    return redirect('courses.announcements.views.list', request.POST.get("course_prefix"), request.POST.get("course_suffix"))

@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode
def save_announcement_order(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))

@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode
def email_announcement(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', course_prefix, course_suffix)
        
    
