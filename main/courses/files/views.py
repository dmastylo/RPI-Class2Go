from django.http import Http404
from django.shortcuts import render
from courses.common_page_data import get_common_page_data
from c2g.models import File
from courses.files.forms import *
from courses.actions import auth_is_course_admin_view_wrapper

@auth_is_course_admin_view_wrapper
def upload(request, course_prefix, course_suffix):

    common_page_data = request.common_page_data
    
    form = FileUploadForm(course=common_page_data['course'])

    return render(request, 'files/upload.html',
            {'common_page_data': common_page_data,
             'form': form,
             })

@auth_is_course_admin_view_wrapper
def edit(request, course_prefix, course_suffix, file_id):

    common_page_data=request.common_page_data

    try:
        file=File.objects.get(id=file_id, course=common_page_data['draft_course'])
    except File.DoesNotExist:
        raise Http404
                         
    form = FileEditForm(instance=file, course=common_page_data['course'])
    return render(request, 'files/upload.html',
                      {'common_page_data': common_page_data,
                      'form': form,
                  })