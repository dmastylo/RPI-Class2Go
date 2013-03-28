from django.http import Http404
from django.shortcuts import render

from c2g.models import File, ContentGroup
from courses.actions import auth_is_course_admin_view_wrapper
from courses.files.forms import *


@auth_is_course_admin_view_wrapper
def upload(request, course_prefix, course_suffix):

    common_page_data = request.common_page_data
    
    form = FileUploadForm(course=common_page_data['course'])

    reverseview = 'courses.files.actions.upload'
    
    return render(request, 'files/upload.html',
            {'reverseview': reverseview,
             'common_page_data': common_page_data,
             'form': form,
             })

@auth_is_course_admin_view_wrapper
def edit(request, course_prefix, course_suffix, file_id):

    common_page_data=request.common_page_data

    try:
        file=File.objects.get(id=file_id, course=common_page_data['draft_course'])
    except File.DoesNotExist:
        raise Http404
                         
    form = FileEditForm(instance=file, course=common_page_data['draft_course'])

    reverseview = 'courses.files.actions.edit'
    cg_info = ContentGroup.groupinfo_by_id('file', file.image.id)
    parent = cg_info.get('__parent', None)
    if not parent:
        parent_val = "none,none"
    else:
        parent_val = "%s,%d" % (cg_info['__parent_tag'], parent.image.id)
    return render(request, 'files/upload.html',
            {'file':file,
             'parent_val':parent_val,
             'reverseview': reverseview,
             'common_page_data': common_page_data,
             'form': form,
             })
