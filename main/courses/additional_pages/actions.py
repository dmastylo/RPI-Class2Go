from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from c2g.models import *
from courses.common_page_data import get_common_page_data
from courses.actions import auth_is_course_admin_view_wrapper


@require_POST
@auth_is_course_admin_view_wrapper
def add(request):
    
    def redirectWithError(warn_msg):
        url = request.get_full_path()
        messages.add_message(request,messages.ERROR, warn_msg)
        return redirect(request.META['HTTP_REFERER'])
    
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

    parent_type, parent_id = None,None
    parent_type = request.POST.get('parent_id')
    if parent_type:
        parent_type,parent_id = parent_type.split(',')
        if parent_type[:4] != 'none':
            parent_id = long(parent_id)

    if request.POST.get("menu_slug") != "":
        index = len(AdditionalPage.objects.filter(course=common_page_data['course'],menu_slug=request.POST.get("menu_slug")))
    else:
        index = section.getNextIndex()
    
    #Validate manually, b/c we didn't use django forms here since we missed it
    try:
        validate_slug(request.POST.get("slug"))
    except ValidationError:
        return redirectWithError("The url descriptor cannot be empty and can only contain numbers, letters, underscores, and hyphens")

    if AdditionalPage.objects.filter(course=common_page_data['course'], slug=request.POST.get("slug")).exists():
        return redirectWithError("A page with this URL identifier already exists")

    if len(request.POST.get("title")) == 0:
        return redirectWithError("The title cannot be empty")

    if len(request.POST.get("title")) > AdditionalPage._meta.get_field("title").max_length:
        return redirectWithError("The title length was too long")

    draft_page = AdditionalPage(course=common_page_data['draft_course'], menu_slug=menu_slug, section=section, title=request.POST.get("title"), slug=request.POST.get("slug"), index=index, mode='draft')
    draft_page.save()
    draft_page.create_ready_instance()
    if parent_type == "none":
        parent_ref = draft_page.image
        ContentGroup.add_parent(parent_ref.course, 'additional_page', parent_ref)
    else:
        parent_ref = ContentGroup.groupable_types[parent_type].objects.get(id=parent_id)
        content_group_groupid = ContentGroup.add_parent(parent_ref.course, parent_type, parent_ref)
        ContentGroup.add_child(content_group_groupid, 'additional_page', draft_page.image, display_style="button")
    
    if request.POST.get("menu_slug") == "":
        return redirect('courses.views.course_materials', course_prefix, course_suffix)
    else:
        return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def save(request):
    def redirectWithError(warn_msg):
        url = request.get_full_path()
        messages.add_message(request,messages.ERROR, warn_msg)
        return redirect(request.META['HTTP_REFERER'])
    
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
    page = AdditionalPage.objects.get(id=request.POST.get("page_id"))
    if request.POST.get("revert") == '1':
        page.revert()
    else:

        #Validate manually, b/c we didn't use django forms here since we missed it
        try:
            validate_slug(request.POST.get("slug"))
        except ValidationError:
            return redirectWithError("The url descriptor cannot be empty and can only contain numbers, letters, underscores, and hyphens")

        if (not page.slug==request.POST.get("slug")) and AdditionalPage.objects.filter(course=common_page_data['course'], slug=request.POST.get("slug")).exists():
            return redirectWithError("A page with this URL identifier already exists")

        if len(request.POST.get("title")) == 0:
            return redirectWithError("The title cannot be empty")

                
        if len(request.POST.get("title")) > AdditionalPage._meta.get_field("title").max_length:
            return redirectWithError("The title length was too long")

        parent_type,parent_id = None,None
        parent_type = request.POST.get('parent')
        if parent_type:
            parent_type,parent_id = parent_type.split(',')
            if parent_type != 'none':
                parent_id = long(parent_id)

        page.title = request.POST.get("title")
        page.description = request.POST.get("description")
        page.slug = request.POST.get("slug")
        page.save()

        ##Also save the production slug per Issue #685, basically slugs are not stageable.
        page.image.slug = request.POST.get("slug")
        page.image.save()

        print "DEBUG: page_id", page.id, "and page.image_id", page.image.id
        print "DEBUG: parent_type", parent_type, "and parent_id", parent_id
        if parent_type == "none" or parent_type == None:           # this is to be a parent
            content_group_groupid = ContentGroup.add_parent(page.image.course, 'additional_page', page.image) # add_parent should handle special cases already
            print "DEBUG: parent type none adds a new ContentGroup entry ", content_group_groupid
        else:
            parent_ref = ContentGroup.groupable_types[parent_type].objects.get(id=parent_id)
            content_group_groupid = ContentGroup.add_parent(parent_ref.course, parent_type, parent_ref)
            ContentGroup.add_child(content_group_groupid, 'additional_page', page.image, display_style="button")

        if request.POST.get("commit") == '1':
            page.commit()
            
    return redirect('courses.additional_pages.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'], page.slug)

@require_POST
@auth_is_course_admin_view_wrapper
def save_order(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
    pages = AdditionalPage.objects.filter(course=common_page_data['draft_course'])
    for page in pages:
        page.index = request.POST.get("order_"+str(page.id))
        page.save()
        prod_page = page.image
        prod_page.index = request.POST.get("order_"+str(page.id))
        prod_page.save()
        
    return redirect(request.META['HTTP_REFERER'])
    
@require_POST
@auth_is_course_admin_view_wrapper
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

