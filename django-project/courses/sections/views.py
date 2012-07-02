from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def list(request, course_id, branch_id):
	return render_to_response('sections/list.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))
	
def admin(request, course_id, branch_id):
	return render_to_response('sections/admin.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))
	
def view(request, course_id, branch_id, section_id):
	return render_to_response('sections/view.html', {'course_id': course_id, 'branch_id': branch_id, 'section_id': section_id, 'request': request}, context_instance=RequestContext(request))
	
def edit(request, course_id, branch_id, section_id):
	return render_to_response('sections/edit.html', {'course_id': course_id, 'branch_id': branch_id, 'section_id': section_id, 'request': request}, context_instance=RequestContext(request))