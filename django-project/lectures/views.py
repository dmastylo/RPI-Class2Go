from django.http import HttpResponse

def list(request, course_id):
	return HttpResponse("These are the lecture for course %s." % course_id)

def view(request, lecture_id):
	return HttpResponse("Viewing lecture number %s." % lecture_id)
