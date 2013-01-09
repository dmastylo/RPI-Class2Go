import json

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from c2g.models import *
from courses.actions import auth_is_course_admin_view_wrapper
from courses.common_page_data import get_common_page_data
from courses.course_materials import get_course_materials


@require_POST
@auth_is_course_admin_view_wrapper
def save_order(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
    sections = ContentSection.objects.filter(course=common_page_data['draft_course'])
    
    for section in sections:
        section.index = request.POST.get("order_"+str(section.id))
        section.save()
        prod_section = section.image
        prod_section.index = request.POST.get("order_"+str(section.id))
        prod_section.save()
        
    return redirect('courses.views.course_materials', request.POST.get("course_prefix"), request.POST.get("course_suffix"))

@require_POST
@auth_is_course_admin_view_wrapper
def rename(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
        
    section = ContentSection.objects.get(id=request.POST.get("section_id"))
    section.title = request.POST.get("title")
    section.save()
    section.commit()
    
    return redirect('courses.views.course_materials', request.POST.get("course_prefix"), request.POST.get("course_suffix"))

@require_POST
@auth_is_course_admin_view_wrapper
def delete_content_section(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
        
    section = ContentSection.objects.get(id=request.POST.get("section_id"))
    section_image = section.image
    section.delete()
    section_image.delete()
    
    return redirect('courses.views.course_materials', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
     
@require_POST
@auth_is_course_admin_view_wrapper
def save_content_order(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
        
    section_structures = get_course_materials(common_page_data=common_page_data, get_video_content=True, get_pset_content=True, get_additional_page_content = True, get_file_content=True, get_exam_content=True)
    
    for section_structure in section_structures:
        if section_structure['section'].id == long(request.POST.get("section_id")):
            for item in section_structure['items']:
                if item['type'] == 'video':
                    item['video'].index = request.POST.get("order_video_"+str(item['video'].id))
                    item['video'].save()
                    video_image = item['video'].image
                    video_image.index = request.POST.get("order_video_"+str(item['video'].id))
                    video_image.save()
                elif item['type'] == 'problem_set':
                    item['problem_set'].index = request.POST.get("order_problem_set_"+str(item['problem_set'].id))
                    item['problem_set'].save()
                    problem_set_image = item['problem_set'].image
                    problem_set_image.index = request.POST.get("order_problem_set_"+str(item['problem_set'].id))
                    problem_set_image.save()
                elif item['type'] == 'additional_page':
                    item['additional_page'].index = request.POST.get("order_additional_page_"+str(item['additional_page'].id))
                    item['additional_page'].save()
                    additional_page_image = item['additional_page'].image
                    additional_page_image.index = request.POST.get("order_additional_page_"+str(item['additional_page'].id))
                    additional_page_image.save()
                elif item['type'] == 'file':
                    item['file'].index = request.POST.get("order_file_"+str(item['file'].id))
                    item['file'].save()
                    file_image = item['file'].image
                    file_image.index = request.POST.get("order_file_"+str(item['file'].id))
                    file_image.save()
                elif item['type'] == 'exam':
                    item['exam'].index = request.POST.get("order_exam_"+str(item['exam'].id))
                    item['exam'].save()
                    exam_image = item['exam'].image
                    exam_image.index = request.POST.get("order_exam_"+str(item['exam'].id))
                    exam_image.save()
            break
            
    return redirect(request.META['HTTP_REFERER'])
    
def get_children(request, section_id, contentgroup_parents_only=False):
    """Return JSON list of type, id, title triples of section_id's children"""
    section = ContentSection.objects.get(id=int(section_id))
    children = []
    l2_kids = []
    if contentgroup_parents_only:
        l2_kids = ContentGroup.get_level2_tag_sorted()
    for child in section.getChildren(gettagged=True, getsorted=True):
        item    = child['item']
        typetag = child['type']
        if contentgroup_parents_only:
            if item.mode != u'ready':
                item = item.image
            if item.id in l2_kids.get(typetag, []):
                continue
        children.append((typetag, item.image.id, item.title))
    return HttpResponse(json.dumps(children), mimetype='application/json')

def get_children_as_contentgroup_parents(request, section_id):
    """Return JSON list of type, id, title triples of section_id's children.
    
    Limit return results to items which are ContentGroup parents.
    """
    return get_children(request, section_id, contentgroup_parents_only=True)
