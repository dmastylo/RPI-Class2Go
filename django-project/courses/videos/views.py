from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response, redirect, HttpResponseRedirect
from django.template import Context, loader
from c2g.models import Course, Video, VideoToExercise, Exercise

from c2g.models import Course, Video, VideoActivity
from courses.common_page_data import get_common_page_data
from courses.course_materials import get_course_materials
import datetime
from courses.videos.forms import *
import gdata.youtube
import gdata.youtube.service

from django.template import RequestContext

def list(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    if 'id' in request.GET:
        #process Video model instance with this youtube id
        #and other stuff
        video = Video.objects.get(pk=request.GET['vid'])
        video.url = request.GET['id']
        video.save()
        video.create_production_instance()

    section_structures = get_course_materials(common_page_data=common_page_data, get_video_content=True, get_pset_content=False)
    
    return render_to_response('videos/'+common_page_data['course_mode']+'/list.html', {'common_page_data': common_page_data, 'section_structures':section_structures, 'context':'video_list'}, context_instance=RequestContext(request))
    
def view(request, course_prefix, course_suffix, slug):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    
    video = None
    video_rec = None
    if request.user.is_authenticated():
        #video = Video.objects.get(course=common_page_data['production_course'], slug=slug)
        video = Video.objects.get(course=common_page_data['course'], slug=slug)
        #video_rec = request.user.videoactivity_set.filter(video=video)
        video_rec = request.user.videoactivity_set.filter(video=video)

    return render_to_response('videos/view.html', {'common_page_data': common_page_data, 'video': video, 'video_rec':video_rec}, context_instance=RequestContext(request))
    
def edit(request, course_prefix, course_suffix, slug):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
        
    video = common_page_data['course'].video_set.all().get(slug=slug)
    form = S3UploadForm(course=common_page_data['course'], instance=video)
    if video.live_datetime:
        live_date = video.live_datetime.strftime('%m/%d/%Y %H:%M')
    else:
        live_date = ''

    return render(request, 'videos/edit.html', 
            {'common_page_data': common_page_data,
             'slug': slug,
             'form': form,
             'live_date': live_date,
             })

def GetOAuth2Url(request):
    client_id = "287022098794.apps.googleusercontent.com"
    redirect_uri = "http://" + request.META['HTTP_HOST'] + "/oauth2callback"
    response_type = "code"
    scope = "https://gdata.youtube.com"

    return "https://accounts.google.com/o/oauth2/auth?client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&scope=" + scope + "&response_type=" + response_type

def GetAuthSubUrl(request):

    next = "http://" + request.META['HTTP_HOST'] + request.path
    scope = 'http://gdata.youtube.com'
    secure = False
    session = True

    yt_service = gdata.youtube.service.YouTubeService()
    return yt_service.GenerateAuthSubURL(next, scope, secure, session)

def upload(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    data = {'common_page_data': common_page_data}

    form = S3UploadForm(course=common_page_data['course'])
    data['form'] = form

    return render_to_response('videos/s3upload.html',
                              data,
                              context_instance=RequestContext(request))


    #OLD YOUTUBE UPLOAD
    if 'token' in request.GET:
        token = request.GET['token']
        data['token'] = token

        yt_service = gdata.youtube.service.YouTubeService()
        #yt_service.developer_key = 'AI39si5GlWcy9S4eVFtajbVZk-DjFEhlM4Zt7CYzJG3f2bwIpsBSaGd8SCWts6V5lbqBHJYXAn73-8emsZg5zWt4EUlJJ4rpQA'
        #yt_service.SetAuthSubToken(token)
        #yt_service.UpgradeToSessionToken()

        yt_logged_in = True
        form = VideoUploadForm(course=common_page_data['course'])
        data['form'] = form
    else:
        # user is not logged into google account for youtube
        yt_logged_in = False
        authSubUrl = GetAuthSubUrl(request)
        #authSubUrl = GetOAuth2Url(request)
        data['authSubUrl'] = authSubUrl

    data['yt_logged_in'] = yt_logged_in
    return render_to_response('videos/upload.html',
                              data,
                              context_instance=RequestContext(request))


def manage_exercises(request, course_prefix, course_suffix, video_slug):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    video = Video.objects.get(course=common_page_data['course'], slug=video_slug)
    videoToExs = VideoToExercise.objects.select_related('exercise', 'video').filter(video=video).order_by('number')
    added_exercises = video.exercise_set.all()
    exercises = Exercise.objects.filter(video__course=common_page_data['course']).exclude(id__in=added_exercises).distinct()
    return render_to_response('videos/manage_exercises.html',
                            {'request': request,
                                'common_page_data': common_page_data,
                                'course_prefix': course_prefix,
                                'course_suffix': course_suffix,
                                'video': video,
                                'videoToExs': videoToExs,
                                'exercises': exercises
                            },
                            context_instance=RequestContext(request))

def add_exercise(request):
#    try:
#        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
#    except:
#        raise Http404

    video = Video.objects.get(id=request.POST['video_id'])
    video_time = request.POST['videotime']

    file_content = request.FILES['exercise']
    file_name = file_content.name

    exercise = Exercise()
    exercise.handle = request.POST['course_prefix'] + '#$!' + request.POST['course_suffix']
    exercise.fileName = file_name
    exercise.file.save(file_name, file_content)
    exercise.save()

    index = len(video.exercise_set.all())
    videoToEx = VideoToExercise(video=video, exercise=exercise, number=index, is_deleted=False, video_time=video_time)
    videoToEx.save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))


def add_existing_exercises(request):
    video = Video.objects.get(id=request.POST['video_id'])
    exercise_ids = request.POST.getlist('exercise')
    exercises = Exercise.objects.filter(id__in=exercise_ids)
    for exercise in exercises:
        video_time = request.POST['videotime_' + str(exercise.id)]
        videoToEx = VideoToExercise(video=video, exercise=exercise, number=len(video.exercise_set.all()), is_deleted=False, video_time=video_time)
        videoToEx.save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))


def save_exercises(request):
    video = Video.objects.get(id=request.POST['video_id'])
    videoToEx = video.videotoexercise_set.all().order_by('number')
    for n in range(0,len(videoToEx)):
        listName = "exercise_order[" + str(n) + "]"
        videoToEx[n].number = request.POST[listName]
        videoToEx[n].save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))



def get_video_exercises(request):
    video = Video.objects.get(id = request.GET['video_id'])
    videoToExs = VideoToExercise.objects.select_related('exercise', 'video').filter(video=video).order_by('number')
    json_list = []
    for videoToEx in videoToExs:
        json_string = "\"" + str(videoToEx.video_time) + "\": {\"time\": " + str(videoToEx.video_time) + ", \"problemDiv\": \"" + str(videoToEx.exercise_id) + "\"}"
        json_list.append(json_string)
     
    json_string = "{" + ','.join( map( str, json_list )) + "}"
    return HttpResponse(json_string)
        
def load_video_problem_set(request, course_prefix, course_suffix, video_id):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    ex_list = Exercise.objects.filter(videotoexercise__video_id=video_id) 
    file_names = []
    for ex in ex_list:
        #Remove the .html from the end of the file name
        file_names.append(ex.fileName[:-5])
    # assessment type is hard-coded because all in-video exercises are formative
    return render_to_response('problemsets/load_problem_set.html',{'file_names': file_names, 'assessment_type': 'formative'},context_instance=RequestContext(request))
