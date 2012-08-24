from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response
from courses.common_page_data import get_common_page_data

from courses.files.forms import *

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
