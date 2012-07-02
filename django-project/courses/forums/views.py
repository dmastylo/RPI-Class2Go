from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def list(request):
	return render_to_response('forums/list.html', {'request': request}, context_instance=RequestContext(request))
	
def admin(request):
	return render_to_response('forums/admin.html', {'request': request}, context_instance=RequestContext(request))
	
def view(request):
	return render_to_response('forums/view.html', {'request': request}, context_instance=RequestContext(request))