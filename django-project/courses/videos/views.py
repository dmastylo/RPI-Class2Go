from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

from c2g.models import Course, Video, VideoTopic

def list(request, course_prefix, course_suffix):
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
        topics = course.videotopic_set.all()
        videos = course.video_set.all()
        return render_to_response('videos/list.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'topics': topics, 'videos': videos, 'request': request}, context_instance=RequestContext(request))

def admin(request, course_prefix, course_suffix):
	return render_to_response('videos/admin.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix, video_id):
	video = Video.objects.get(id=video_id)
	return render_to_response('videos/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'video': video, 'request': request}, context_instance=RequestContext(request))
	
def edit(request, course_prefix, course_suffix, video_id):
	return render_to_response('videos/edit.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'video_id': video_id, 'request': request}, context_instance=RequestContext(request))

def save(request):
	video_id = request.POST['video_id']
	playTime = request.POST['playTime']
	video = Video.objects.get(id=video_id)
	video.start_seconds = playTime
	video.save()
	return HttpResponse("saved")
