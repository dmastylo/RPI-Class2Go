from django.http import HttpResponse

def list(request, course_id):
	return HttpResponse("These are the forums for course %s." % course_id)

def view(request, forum_id):
	return HttpResponse("Viewing forum number %s." % forum_id)
