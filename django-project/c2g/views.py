from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
import json

from django.contrib.sites.models import Site
import settings

from c2g.db_test_data import *

### C2G Core Views ###

def home(request):
	layout = {'l': 200, 'm': 800, 'r': 200}
	return render_to_response('base.html', {'SITE_URL': Site.objects.get_current().domain, 'STATIC_URL': settings.STATIC_URL, 'layout': json.dumps(layout), 'request': request}, context_instance=RequestContext(request))


def db_populate(request):
        layout = {'l': 200, 'm': 800, 'r': 200}

        #Defining settings here for now in the absence of a form
        delete_current_data = 1
        create_institution_data = 1
        create_course_data = 1
        create_user_data = 1

        if delete_current_data == 1:
                delete_db_data()

        if create_institution_data == 1:
                create_institutions(create_course_data, create_user_data)


        return render_to_response('base.html', {'SITE_URL': Site.objects.get_current().domain, 'STATIC_URL': settings.STATIC_URL, 'layout': json.dumps(layout), 'request': request}, context_instance=RequestContext(request))

