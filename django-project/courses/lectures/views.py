from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def list(request, course_prefix, course_suffix):
	return render_to_response('lectures/list.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def admin(request, course_prefix, course_suffix):
	return render_to_response('lectures/admin.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix, lecture_id):
	return render_to_response('lectures/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'lecture_id': lecture_id,'request': request}, context_instance=RequestContext(request))
	
def edit(request, course_prefix, course_suffix, lecture_id):
	return render_to_response('lectures/edit.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'lecture_id': lecture_id, 'request': request}, context_instance=RequestContext(request))