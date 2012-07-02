from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

def list(request):
	return render_to_response('files/list.html', {'request': request}, context_instance=RequestContext(request))
	
def admin(request):
	return render_to_response('files/admin.html', {'request': request}, context_instance=RequestContext(request))