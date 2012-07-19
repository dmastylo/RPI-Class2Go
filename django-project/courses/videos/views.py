from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

from c2g.models import Course, Video, VideoTopic, VideoActivity

def list(request, course_prefix, course_suffix):
    course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    data = {'request': request,
	    'course_prefix': course_prefix,
	    'course_suffix': course_suffix,
	    'course': course,
	   }

    if request.user.is_authenticated():
        data['topics'] = course.videotopic_set.all()
        data['videoRecs'] = request.user.videoactivity_set.filter(course=course)

    return render_to_response('videos/list.html', 
			      data, 
			      context_instance=RequestContext(request))

def admin(request, course_prefix, course_suffix):
    course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    return render_to_response('videos/admin.html', 
            {'request': request,
             'course_prefix': course_prefix, 
             'course_suffix': course_suffix, 
             'course': course, 
             }, 
            context_instance=RequestContext(request))
    
def view(request, course_prefix, course_suffix, video_id):
    course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    data = {'request': request,
	    'course_prefix': course_prefix,
	    'course_suffix': course_suffix,
	    'course': course,
	   }

    if request.user.is_authenticated():
        data['videoRec'] = request.user.videoactivity_set.get(video=video_id)
    #video = Video.objects.get(id=video_id)

    return render_to_response('videos/view.html', 
                              data,
                              context_instance=RequestContext(request))
    
def edit(request, course_prefix, course_suffix, video_id):
    course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    return render_to_response('videos/edit.html', 
            {'request': request,
             'course_prefix': course_prefix, 
             'course_suffix': course_suffix, 
             'course': course, 
             'video_id': video_id, 
             }, 
            context_instance=RequestContext(request))

def save(request):
    videoRec = request.POST['videoRec']
    playTime = request.POST['playTime']
    video = VideoActivity.objects.get(id=videoRec)
    video.start_seconds = playTime
    video.save()
    return HttpResponse("saved")
