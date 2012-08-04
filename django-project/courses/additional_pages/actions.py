from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
import re

def add(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    
    index = len(AdditionalPage.objects.filter(course=common_page_data['course']))
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.view', course_prefix, course_suffix)
    
    staging_page = AdditionalPage(course=common_page_data['staging_course'], title=request.POST.get("title"), slug=request.POST.get("slug"), index=index, mode='staging')
    staging_page.save()
    
    staging_page.create_production_instance()
    
    return redirect(request.META['HTTP_REFERER'])
    
def save(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
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
    
def delete(request):
    pass
    
    