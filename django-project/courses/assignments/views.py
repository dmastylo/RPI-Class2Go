from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def list(request, course_prefix, course_suffix):
	return render_to_response('assignments/list.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def admin(request, course_prefix, course_suffix):
	return render_to_response('assignments/admin.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix, assignment_id):
	return render_to_response('assignments/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'assignment_id':assignment_id, 'request': request}, context_instance=RequestContext(request))
	
def edit(request, course_prefix, course_suffix, assignment_id):
	return render_to_response('assignments/edit.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'assignment_id':assignment_id, 'request': request}, context_instance=RequestContext(request))
	
def grade(request, course_prefix, course_suffix, assignment_id):
	return render_to_response('assignments/grade.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'assignment_id':assignment_id, 'request': request}, context_instance=RequestContext(request))
