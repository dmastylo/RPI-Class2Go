from django.http import Http404
from django.shortcuts import render, redirect

from c2g.models import ContentGroup
from courses.actions import auth_is_course_admin_view_wrapper, create_contentgroup_entries_from_post
from courses.common_page_data import get_common_page_data
from courses.files.forms import *


@auth_is_course_admin_view_wrapper
def upload(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)

    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES, course=common_page_data['course'])
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.course = common_page_data['course']
            new_file.index = new_file.section.getNextIndex()
            new_file.mode = 'draft'
            new_file.handle = course_prefix + "--" + course_suffix

            new_file.save()
            new_file.create_ready_instance()

            create_contentgroup_entries_from_post(request, 'parent', new_file.image, 'file', request.POST.get('display_style'))

            return redirect('courses.views.course_materials', course_prefix, course_suffix)
    else:
        form = FileUploadForm(course=common_page_data['course'])
        reverseview = 'courses.files.actions.upload'

    return render(request, 'files/upload.html',
            {'reverseview':reverseview,
             'common_page_data': common_page_data,
             'form': form,
             })

@auth_is_course_admin_view_wrapper
def edit(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    file_id = request.POST.get("file_id","-1")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    try:
        file=File.objects.get(id=int(file_id), course=common_page_data['draft_course'])
    except File.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = FileEditForm(request.POST, course=common_page_data['draft_course'], instance=file)
        if form.is_valid():
            form.save()
            file.commit()
            
            parent_type = request.POST.get('parent')
            if parent_type and parent_type[:4] != 'none':
                parent_type, parent_id = parent_type.split(',')
            else:
                parent_type, parent_id = None, None
            if parent_type:
                parent_ref = ContentGroup.groupable_types[parent_type].objects.get(id=long(parent_id)).image
                content_group_groupid = ContentGroup.add_parent(file.image.course, parent_type, parent_ref.image)
                ContentGroup.add_child(content_group_groupid, 'file', file.image, display_style=request.POST.get('display_style'))
            else: #file should have no parents, so delete its place in a contentgroup if it's a child
                try:
                    cgobj = file.image.contentgroup_set.get()
                    if cgobj.level != 1:
                        cgobj.delete()
                except ContentGroup.DoesNotExist: #nothing to do if the file is not in a contentgroup
                    pass
            return redirect('courses.views.course_materials', course_prefix, course_suffix)
    else:
        form = FileEditForm(instance=file, course=common_page_data['course'])

    reverseview = 'courses.files.actions.edit'
    cg_info = ContentGroup.groupinfo_by_id('file', file.image.id)
    parent = cg_info.get('__parent', None)
    if not parent:
        parent_val = "none,none"
    else:
        parent_val = "%s,%d" % (cg_info['__parent_tag'], parent.id)

    return render(request, 'files/upload.html',
                  {'file':file,
                  'parent_val':parent_val,
                  'reverseview': reverseview,
                  'common_page_data': common_page_data,
                  'form': form,
                  })

@auth_is_course_admin_view_wrapper
def delete_file(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404

    file = File.objects.get(id=request.POST.get("file_id"))
    file.delete()
    file.image.delete()

    return redirect(request.META['HTTP_REFERER'])
