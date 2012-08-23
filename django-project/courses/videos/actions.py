from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from c2g.models import Course, Video
from django.template import RequestContext
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse

from c2g.models import Course, Video, VideoActivity
from courses.common_page_data import get_common_page_data

from courses.videos.forms import *
import gdata.youtube
import gdata.youtube.service
import urllib2, urllib, json
import re

from datetime import datetime
from courses.actions import auth_view_wrapper
from django.views.decorators.http import require_POST
    
### Videos ###

@require_POST
@auth_view_wrapper
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

@require_POST
@auth_view_wrapper
def edit_video(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    slug = request.POST.get("video_slug")

    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', course_prefix, course_suffix)

    if request.method == 'POST':
        video = common_page_data['course'].video_set.all().get(slug=slug)

        action = request.POST['action']
        if action == "Revert":
            video.revert()
            form = S3UploadForm(course=common_page_data['course'], instance=video)
        else:
            form = S3UploadForm(request.POST, request.FILES, course=common_page_data['course'], instance=video)
            if form.is_valid():
                form.save()
                if action == "Save and Publish":
                    video.commit()
                return redirect('courses.videos.views.list', course_prefix, course_suffix)

    return render(request, 'videos/edit.html',
                  {'common_page_data': common_page_data,
                   'slug': slug,
                   'form': form,
                   })

@require_POST
@auth_view_wrapper
def delete_video(request):
    try:
        common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    except:
        raise Http404
        
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', request.POST.get("course_prefix"), request.POST.get("course_suffix"))
        
    video = Video.objects.get(id=request.POST.get("video_id"))
    video.delete()
    video.image.delete()
    
    return redirect(request.META['HTTP_REFERER'])
    
@require_POST
@auth_view_wrapper
def save_video_progress(request):
    videoRec = request.POST['videoRec']
    playTime = request.POST['playTime']
    video = VideoActivity.objects.get(id=videoRec)
    video.start_seconds = playTime
    video.save()
    return HttpResponse("saved")

def oauth(request):
    if 'code' in request.GET:
        code = request.GET.get('code')
#        print code
        client_id = "287022098794.apps.googleusercontent.com"
        client_secret = "vqCgk8qv1XKKtiKGfR8vTq_w"
        redirect_uri = "http://" + request.META['HTTP_HOST'] + "/oauth2callback"

        post_data = [('code', code), ('client_id', client_id), ('client_secret', client_secret), ('redirect_uri', redirect_uri), ('grant_type', 'authorization_code')]
        result = urllib2.urlopen('https://accounts.google.com/o/oauth2/token', urllib.urlencode(post_data))
        content = json.loads(result.read())

        yt_service = gdata.youtube.service.YouTubeService(additional_headers={'Authorization': "Bearer "+content['access_token']})
        yt_service.developer_key = 'AI39si5GlWcy9S4eVFtajbVZk-DjFEhlM4Zt7CYzJG3f2bwIpsBSaGd8SCWts6V5lbqBHJYXAn73-8emsZg5zWt4EUlJJ4rpQA'


        video = Video.objects.get(pk=request.GET.get('state'))
        
        my_media_group = gdata.media.Group(
            title=gdata.media.Title(text=video.title),
            description=gdata.media.Description(description_type='plain',
                                                text=video.description),
            category=[gdata.media.Category(
                    text='Education',
                    label='Education')],
            )

        video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)

        entry = yt_service.InsertVideoEntry(video_entry, video.file)
        #print entry.id.ToString()
        match = re.search('http://gdata.youtube.com/feeds/api/videos/([a-zA-Z0-9_-]+)</ns0:id>', entry.id.ToString())
        #print match.group(1)
        video.url = match.group(1)
        video.duration = entry.media.duration.seconds
        video.save()
        video.image.url = video.url
        video.image.duration = video.duration
        video.image.save()

        parts = str(video.handle).split("#$!")
        return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(parts[0], parts[1], video.slug)))
    
#    return redirect('courses.videosviews.list', course_prefix, course_suffix)
    #return redirect("http://" + request.META['HTTP_HOST'] + "/nlp/Fall2012/videos")

def GetOAuth2Url(request, video):
    client_id = "287022098794.apps.googleusercontent.com"
    redirect_uri = "http://" + request.META['HTTP_HOST'] + "/oauth2callback"
    response_type = "code"
    scope = "https://gdata.youtube.com"
    state = str(video.id)

    return "https://accounts.google.com/o/oauth2/auth?client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&scope=" + scope + "&response_type=" + response_type + "&state=" + state

@require_POST
@auth_view_wrapper
def upload(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)

    data = {'common_page_data': common_page_data}

    if request.method == 'POST':
        new_video = Video(course=common_page_data['course'])
        form = S3UploadForm(request.POST, request.FILES, course=common_page_data['course'], instance=new_video)
        if form.is_valid():
            new_video = form.save(commit=False)
            new_video.index = new_video.section.getNextIndex()
            new_video.mode = 'staging'
            new_video.handle = course_prefix + "#$!" + course_suffix

            # Bit of jiggery pokery to so that the id is set when the upload_path function is called.
            # Now storing file with id appended to the file path so that thumbnail and associated manifest files
            # are easily associated with the video by putting them all in the same directory.
            new_video.file = None
            new_video.save()
            new_video.file = form.cleaned_data['file']
            
            new_video.save()
            new_video.create_production_instance()
            print new_video.file.url

            authUrl = GetOAuth2Url(request, new_video)
            #eventually should store an access token, so they don't have to give permission everytime
            return redirect(authUrl)
        #    return redirect("http://" + request.META['HTTP_HOST'])
        
    
    else:
        form = S3UploadForm(course=common_page_data['course'])
    data['form'] = form

    return render_to_response('videos/s3upload.html',
                              data,
                              context_instance=RequestContext(request))
