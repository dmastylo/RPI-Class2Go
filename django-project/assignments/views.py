from django.http import HttpResponse

def list(request, course_id):
	return HttpResponse("This is the list of assignments for course %s." % course_id)

def view(request, assignment_id):
	return HttpResponse("This is assignment %s." % assignment_id)

def grade(request, assignment_id):
	return HttpResponse("This is your grade for assignment %s." % assignment_id)
