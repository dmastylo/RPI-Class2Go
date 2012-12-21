from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from courses.actions import auth_is_course_admin_view_wrapper
from courses.common_page_data import get_common_page_data
from courses.exams.forms import *

@auth_is_course_admin_view_wrapper
def delete_exam(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404

    exam = Exam.objects.get(id=request.POST.get("exam_id"))
    exam.delete()
    exam.image.delete()

    return redirect(request.META['HTTP_REFERER'])
