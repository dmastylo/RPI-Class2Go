from django.http import HttpResponse
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
				'width': 200,
				'content': "<span style='color: red;'>Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column... Left_column</span>",
			},
			'm': {
				#'width': 800,
				'min-width': 400,
				'max-width': 800,
				'content': "<span style='color: green;'>Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column... Middle_column</span>",
			},
			'r': {
				'width': 200,
				'content': "<span style='color: red;'>Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column... Right_column</span>",
			},
		},
	}
	
	html = GenPageHTML(head, body)
	return HttpResponse(html)
