from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from courses.common_page_data import get_common_page_data
	
def admin(request, course_prefix, course_suffix):
    return render_to_response('forums/admin.html', {'common_page_data': common_page_data}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix):
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    return render_to_response('forums/view.html', {'common_page_data': common_page_data}, context_instance=RequestContext(request))