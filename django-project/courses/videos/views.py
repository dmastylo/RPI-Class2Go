from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

from c2g.models import Video, VideoTopic

def list(request, course_id, branch_id):
	topics = VideoTopic.objects.all()
	return render_to_response('videos/list.html', {'course_id': course_id, 'branch_id': branch_id, 'topics': topics, 'request': request}, context_instance=RequestContext(request))
	#return render_to_response('videos/list.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))
	
def admin(request, course_id, branch_id):
	return render_to_response('videos/admin.html', {'course_id': course_id, 'branch_id': branch_id, 'request': request}, context_instance=RequestContext(request))
	
def view(request, course_id, branch_id, video_id):
	video = Video.objects.get(id=video_id)
	return render_to_response('videos/view.html', {'course_id': course_id, 'branch_id': branch_id, 'video': video, 'request': request}, context_instance=RequestContext(request))
	
def edit(request, course_id, branch_id, video_id):
	return render_to_response('videos/edit.html', {'course_id': course_id, 'branch_id': branch_id, 'video_id': video_id, 'request': request}, context_instance=RequestContext(request))
