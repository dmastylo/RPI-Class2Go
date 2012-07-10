from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def list(request, course_prefix, course_suffix):
	return render_to_response('sections/list.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def admin(request, course_prefix, course_suffix):
	return render_to_response('sections/admin.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix, section_id):
	return render_to_response('sections/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'section_id': section_id, 'request': request}, context_instance=RequestContext(request))
	
def edit(request, course_prefix, course_suffix, section_id):
	return render_to_response('sections/edit.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'section_id': section_id, 'request': request}, context_instance=RequestContext(request))