from django.http import Http404
from django.shortcuts import render
from courses.common_page_data import get_common_page_data

from courses.files.forms import *
from courses.actions import auth_is_course_admin_view_wrapper

@auth_is_course_admin_view_wrapper
def upload(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    form = FileUploadForm(course=common_page_data['course'])

    return render(request, 'files/upload.html',
            {'common_page_data': common_page_data,
             'form': form,
             })
