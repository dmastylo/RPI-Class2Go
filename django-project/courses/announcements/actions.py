from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.common_page_data import get_common_page_data
from courses.actions import auth_view_wrapper
from django.views.decorators.http import require_POST

@require_POST
@auth_view_wrapper
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
        mode='staging',
        owner=request.user,
    )
    announcement.save()
    
    announcement.create_production_instance()
    
    if request.POST.get("commit") == '1':
        announcement.commit()
    
    return redirect(request.META['HTTP_REFERER'])
    
@require_POST
@auth_view_wrapper
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
@auth_view_wrapper
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
@auth_view_wrapper    
def save_announcement_order(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))

@require_POST
@auth_view_wrapper
def email_announcement(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', course_prefix, course_suffix)
        
    