from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from c2g.models import Course, Video
from django.template import RequestContext

from c2g.models import Video, VideoTopic

def list(request, course_prefix, course_suffix):
    course_handle = course_prefix + "-" + course_suffix
    course = Course.objects.get(handle=course_handle)
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    
    f = open("C:/c2g_filestore/"+course_prefix+"-"+course_suffix+"/production/video_list.html","r")
    raw_m_content = f.read();
    f.close()
	
    topics = VideoTopic.objects.all()
    return render_to_response('videos/list.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'l_content': l_content, 'm_content': m_content, 'topics': topics, 'request': request}, context_instance=RequestContext(request))
	
def admin(request, course_prefix, course_suffix):
	return render_to_response('videos/admin.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix, video_id):
	video = Video.objects.get(id=video_id)
	return render_to_response('videos/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'video': video, 'request': request}, context_instance=RequestContext(request))
	
def edit(request, course_prefix, course_suffix, video_id):
	return render_to_response('videos/edit.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'video_id': video_id, 'request': request}, context_instance=RequestContext(request))
