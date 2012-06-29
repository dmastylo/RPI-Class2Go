from django.http import HttpResponse

def all(request):
	return HttpResponse("Here are all the courses.")

def current(request):
	return HttpResponse("Here are you current courses.")

def edit(request, course_id):
	return HttpResponse("Editing course %s." % course_id)

def members(request, course_id):
	return HttpResponse("There are the members of course %s." % course_id)

def mine(request):
	return HttpResponse("This is my course.")

def new(request):
	return HttpResponse("Adding a new course.")

def view(request, course_id):
	return HttpResponse("Viewing course %s." %course_id)
