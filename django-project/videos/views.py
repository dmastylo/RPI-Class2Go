from django.http import HttpResponse

def list(request, course_id):
	return HttpResponse("These are the videos for course %s." % course_id)

def view(request, video_id):
	return HttpResponse("Viewing video number %s." % video_id)
