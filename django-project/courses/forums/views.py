from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
<<<<<<< HEAD
from courses.common_page_data import get_common_page_data
	
def admin(request, course_prefix, course_suffix):
    return render_to_response('forums/admin.html', {'common_page_data': common_page_data}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix):
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    return render_to_response('forums/view.html', {'common_page_data': common_page_data}, context_instance=RequestContext(request))
=======
    
def admin(request, course_prefix, course_suffix):
    return render_to_response('forums/admin.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
    
def view(request, course_prefix, course_suffix):
    return render_to_response('forums/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
>>>>>>> 718741d3c4d9a71e19c4579a2cc1f30c927fea0f
