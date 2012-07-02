from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def all(request):
	return render_to_response('courses/all.html', {'request': request}, context_instance=RequestContext(request))
	
def current(request):
	return render_to_response('courses/current.html', {'request': request}, context_instance=RequestContext(request))
	
def mine(request):
	return render_to_response('courses/mine.html', {'request': request}, context_instance=RequestContext(request))
	
def view(request):
	return render_to_response('courses/view.html', {'request': request}, context_instance=RequestContext(request))
