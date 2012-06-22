from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
import json

import c2g.lib.page_factory
import c2g.templates.core.topbars

from django.contrib.sites.models import Site
import settings

SITE_URL = Site.objects.get_current().domain
STATIC_URL = settings.STATIC_URL
GenPageHTML = c2g.lib.page_factory.GenPageHTML
GenTopbar = c2g.templates.core.topbars.GenTopbar

### C2G Core Views ###

def home(request):
	head = {
		'css':[],
		'script_srcs':[],
	}
	
	body = {
		'topbar': GenTopbar({'type': 'landing_page'}),
		
		'content': {
			'l': {
				'content': "<span style='color: red;'>Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column</span>",
			},
			'm': {
				'content': "<span style='color: green;'>Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column</span>",
			},
			'r': {
				'content': "<span style='color: red;'>Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column</span>",
			},
		},
	}
	
	#html = GenPageHTML(head, body)
	#return HttpResponse(html)
	layout = {'l': 200, 'm': 800, 'r': 200}
	return render_to_response('base.html', {'SITE_URL': SITE_URL, 'STATIC_URL': STATIC_URL, 'head': head, 'body': body, 'layout': json.dumps(layout), 'request': request}, context_instance=RequestContext(request))