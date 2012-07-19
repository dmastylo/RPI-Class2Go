from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Video, VideoTopic

def list(request, course_prefix, course_suffix):
    course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    topics = VideoTopic.objects.all()
    videos = course.video_set.all()
    return render_to_response('videos/list.html', 
            {'request': request,
             'course_prefix': course_prefix, 
             'course_suffix': course_suffix, 
             'course': course, 
             'videos': videos,
             'topics': topics, 
             }, 
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
    video = Video.objects.get(id=video_id)
    return render_to_response('videos/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'video': video, 'request': request}, context_instance=RequestContext(request))
    return render_to_response('videos/view.html', 
            {'request': request,
             'course_prefix': course_prefix, 
             'course_suffix': course_suffix, 
             'course': course, 
             'video': video, 
             }, 
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
     video_id = request.POST['video_id']
     playTime = request.POST['playTime']
     video = Video.objects.get(id=video_id)
     video.start_seconds = playTime
     video.save()
     return HttpResponse("saved")
