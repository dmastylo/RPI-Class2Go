from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

### C2G Core Views ###

def home(request):
	return render_to_response('base.html', {'request': request}, context_instance=RequestContext(request))