from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from django.contrib.auth.models import User,Group
from courses.common_page_data import get_common_page_data
from c2g.models import *
from courses.actions import auth_view_wrapper
from django.views.decorators.http import require_POST

@require_POST
@auth_view_wrapper
def delete_problemset(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
        
    problemset = ProblemSet.objects.get(id=request.POST.get("problem_set_id"))
    problemset.delete()
    problemset.image.delete()
    
    return redirect(request.META['HTTP_REFERER'])
    
