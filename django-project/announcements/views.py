from django.http import HttpResponse

def list(request, course_id=-1):
	return HttpResponse("This is the annoucements list.")
