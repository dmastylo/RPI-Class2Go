from django.http import HttpResponse

def list(request, course_id):
	return HttpResponse("These are the sections for course %s." % course_id)

def view(request, section_id):
	return HttpResponse("Viewing section number %s." % section_id)
