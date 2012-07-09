from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement

def admin(request, course_id, branch_id):
    return render_to_response('branches/admin.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))

def members(request, course_id, branch_id):
    return render_to_response('branches/members.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))

def view(request, course_id, branch_id):
#    course = Course.objects.get(course_prefix=course_id, course_instance=branch_id)
#    announcement_list = course.announcement_set.all()
    return render_to_response('branches/view.html', {'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))
