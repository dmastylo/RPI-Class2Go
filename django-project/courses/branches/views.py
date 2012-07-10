from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement, NewsEvent

def admin(request, course_id, branch_id):
    return render_to_response('branches/admin.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))

def members(request, course_id, branch_id):
    return render_to_response('branches/members.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))

def view(request, course_id, branch_id):
    try:
        course = Course.objects.get(handle=course_id+"-"+branch_id)
    except:
        raise Http404
    announcement_list = course.announcement_set.all().order_by('-time_created')
    news_list = course.newsevent_set.all().order_by('-time_created')[0:5]
    return render_to_response('branches/view.html', {'course': course, 'announcement_list': announcement_list, 'news_list': news_list, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))
