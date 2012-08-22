from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
import re
from courses.actions import auth_view_wrapper
from django.views.decorators.http import require_POST

@require_POST
@auth_view_wrapper
def add(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.view', course_prefix, course_suffix)
    
    menu_slug = None
    if request.POST.get("menu_slug") != "":
        menu_slug = request.POST.get("menu_slug")
        
    section = None
    if request.POST.get("section_id") != "":
        section = ContentSection.objects.get(id=request.POST.get("section_id"))
    
    if request.POST.get("menu_slug") != "":
        index = len(AdditionalPage.objects.filter(course=common_page_data['course'],menu_slug=request.POST.get("menu_slug")))
    else:
        index = section.getNextIndex()
        
    staging_page = AdditionalPage(course=common_page_data['staging_course'], menu_slug=menu_slug, section=section, title=request.POST.get("title"), slug=request.POST.get("slug"), index=index, mode='staging')
    staging_page.save()
    
    staging_page.create_production_instance()
    
    if request.POST.get("menu_slug") == "":
        return redirect('courses.views.course_materials', course_prefix, course_suffix)
    else:
        return redirect(request.META['HTTP_REFERER'])
    
@require_POST
@auth_view_wrapper
def save(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
    page = AdditionalPage.objects.get(id=request.POST.get("page_id"))
    if request.POST.get("revert") == '1':
        page.revert()
    else:
        page.title = request.POST.get("title")
        page.description = request.POST.get("description")
        page.slug = request.POST.get("slug")
        page.save()
        
        if request.POST.get("commit") == '1':
            page.commit()
            
    return redirect('courses.additional_pages.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'], page.slug)

@require_POST
@auth_view_wrapper
def save_order(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
    pages = AdditionalPage.objects.filter(course=common_page_data['staging_course'])
    for page in pages:
        page.index = request.POST.get("order_"+str(page.id))
        page.save()
        prod_page = page.image
        prod_page.index = request.POST.get("order_"+str(page.id))
        prod_page.save()
        
    return redirect(request.META['HTTP_REFERER'])
    
@require_POST
@auth_view_wrapper
def delete(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
        
    page_id = request.POST.get("page_id")
    page = AdditionalPage.objects.get(id=page_id)
    if page.slug == 'overview':
        return
        
    page.delete()
    if page.image:
        page.image.delete()
    
    return redirect(request.META['HTTP_REFERER'])