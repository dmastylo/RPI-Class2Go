from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

from c2g.db_test_data import *

### C2G Core Views ###

def home(request):
	return render_to_response('base.html', {'request': request}, context_instance=RequestContext(request))

def db_populate(request):
	#Defining settings here for now in the absence of a form
	delete_current_data = 1
	create_institution_data = 0
	create_course_data = 0
	create_user_data = 0
	create_nlp_course_data = 1

	if delete_current_data == 1:
		delete_db_data()

	if create_institution_data == 1:
		create_institutions(create_course_data, create_user_data)

	if create_nlp_course_data == 1:
		create_nlp_course()

	return render_to_response('base.html', {'request': request}, context_instance=RequestContext(request))
