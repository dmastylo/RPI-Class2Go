from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
import json

from django.contrib.sites.models import Site
import settings

### C2G Core Views ###

def home(request):
	layout = {'l': 200, 'm': 800, 'r': 200}
	return render_to_response('base.html', {'layout': json.dumps(layout), 'request': request}, context_instance=RequestContext(request))