from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from c2g.models import Course, Video
from django.template import RequestContext

from c2g.models import Course, Video, VideoActivity
from courses.common_page_data import get_common_page_data

import datetime

### Video Topics ###

def add_video_topic(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    
    index = len(VideoTopic.objects.filter(course=common_page_data['course']))
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.view', course_prefix, course_suffix)
    
    staging_video_topic = VideoTopic(course=common_page_data['staging_course'], title=request.POST.get("title"), index=index, mode='staging')
    staging_video_topic.save()
    staging_video_topic.create_production_instance()
    
    return redirect(request.META['HTTP_REFERER'])

def edit_video_topic(request):
    pass
    
### Videos ###

def add_video(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.view', course_prefix, course_suffix)
    
    index = len(Video.objects.filter(topic_id=request.POST.get("topic_id")))
    
    staging_video = Video(
        course=common_page_data['staging_course'],
        topic_id=int(request.POST.get("topic_id")),
        title=request.POST.get("title"),
        #description=request.POST.get("description"),
        type='youtube',
        url=request.POST.get("yt_id"),
        slug=request.POST.get("slug"),
        mode='staging',
        index=index
    )
    staging_video.save()
    staging_video.create_production_instance()
    
    return redirect(request.META['HTTP_REFERER'])

def commit(request):
    ids = request.POST.get("commit_ids").split(",")
    for id in ids:
        Video.objects.get(id=id).commit()
    return redirect(request.META['HTTP_REFERER'])
    
def revert(request):
    ids = request.POST.get("revert_ids").split(",")
    for id in ids:
        Video.objects.get(id=id).commit()
    return redirect(request.META['HTTP_REFERER'])
    
def change_live_datetime(request):
    ids = request.POST.get("change_live_datetime_ids").split(",")
    
    for id in ids:
        image = Video.objects.get(id=id).image
        if request.POST.get("live_datetime_option") == 'now':
            image.live_datetime = datetime.datetime.now()
        else:
            live_date_parts = request.POST.get("live_date").split("-")
            year = int(live_date_parts[2])
            month = int(live_date_parts[0])
            day = int(live_date_parts[1])
            if request.POST.get("live_hours") == '':
                hour = 0
            else:
                hour = int(request.POST.get("live_hours"))
                
            if request.POST.get("live_minutes") == '':
                minute = 0
            else:
                minute = int(request.POST.get("live_minutes"))
            
            image.live_datetime = datetime.datetime(year,month,day,hour,minute)
        
        image.save()
    return redirect(request.META['HTTP_REFERER'])

def edit_video(request):
    pass
    
def save_video_progress(request):
    videoRec = request.POST['videoRec']
    playTime = request.POST['playTime']
    video = VideoActivity.objects.get(id=videoRec)
    video.start_seconds = playTime
    video.save()
    return HttpResponse("saved")