from django.http import HttpResponse

def list(request, course_id):
	return HttpResponse("These are the office hours for course %s." % course_id)
