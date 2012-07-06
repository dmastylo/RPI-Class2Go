from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement

def all(request):
	#course_list = Course.objects.all()
	#return render_to_response('courses/all.html', {'request': request, 'course_list': course_list}, context_instance=RequestContext(request))
	return render_to_response('courses/all.html', {'request': request}, context_instance=RequestContext(request))
	
def current(request):
	return render_to_response('courses/current.html', {'request': request}, context_instance=RequestContext(request))
	
def mine(request):
	return render_to_response('courses/mine.html', {'request': request}, context_instance=RequestContext(request))
	
def view(request, course_id):
    announcement_list = Announcement.objects.all().order_by('-last_updated')
    return render_to_response('courses/view.html', {'course_id': course_id, 'announcement_list': announcement_list, 'request': request}, context_instance=RequestContext(request))
