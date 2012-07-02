from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def list(request):
	return render_to_response('assignments/list.html', {'request': request}, context_instance=RequestContext(request))
	
def admin(request):
	return render_to_response('assignments/admin.html', {'request': request}, context_instance=RequestContext(request))
	
def view(request):
	return render_to_response('assignments/view.html', {'request': request}, context_instance=RequestContext(request))
	
def edit(request):
	return render_to_response('assignments/edit.html', {'request': request}, context_instance=RequestContext(request))
	
def grade(request):
	return render_to_response('assignments/grade.html', {'request': request}, context_instance=RequestContext(request))