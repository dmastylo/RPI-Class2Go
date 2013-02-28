from django.shortcuts import redirect

from courses.actions import always_switch_mode, auth_is_course_admin_view_wrapper
from courses.exams.forms import *


@auth_is_course_admin_view_wrapper
@always_switch_mode
def delete_exam(request):
    exam = Exam.objects.get(id=request.POST.get("exam_id"))
    exam.delete()
    exam.image.delete()
    return redirect(request.META['HTTP_REFERER'])
