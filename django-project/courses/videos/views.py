from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
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
        video = Video.objects.get(course=common_page_data['production_course'], slug=slug)
        #video_rec = request.user.videoactivity_set.filter(video=video)
        video_rec = request.user.videoactivity_set.filter(video=video)

    return render_to_response('videos/view.html', {'common_page_data': common_page_data, 'video': video, 'video_rec':video_rec}, context_instance=RequestContext(request))
    
def edit(request, course_prefix, course_suffix, video_id):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
        
    return render_to_response('videos/edit.html', 
            {'request': request,
             'course_prefix': course_prefix,
             'course_suffix': course_suffix,
             'course': course,
             'video_id': video_id,
             },
            context_instance=RequestContext(request))

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

    pset = ProblemSet.objects.get(id=request.POST['pset_id'])

    file_content = request.FILES['exercise']
    file_name = file_content.name

    exercise = Exercise()
    exercise.handle = request.POST['course_prefix'] + '-' + request.POST['course_suffix']
    exercise.fileName = file_name
    exercise.file.save(file_name, file_content)
    exercise.save()

    index = len(pset.exercise_set.all())
    psetToEx = ProblemSetToExercise(problemSet=pset, exercise=exercise, number=index, is_deleted=False)
    psetToEx.save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], pset.slug,)))


def add_existing_exercises(request):
    pset = ProblemSet.objects.get(id=request.POST['pset_id'])
    exercise_ids = request.POST.getlist('exercise')
    exercises = Exercise.objects.filter(id__in=exercise_ids)
    for exercise in exercises:
        psetToEx = ProblemSetToExercise(problemSet=pset, exercise=exercise, number=len(pset.exercise_set.all()), is_deleted=False)
        psetToEx.save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], pset.slug,)))


def save_exercises(request):
    pset = ProblemSet.objects.get(id=request.POST['pset_id'])
    psetToEx = pset.problemsettoexercise_set.all().order_by('number')
    for n in range(0,len(psetToEx)):
        listName = "exercise_order[" + str(n) + "]"
        psetToEx[n].number = request.POST[listName]
        psetToEx[n].save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], pset.slug,)))

def list(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    section_structures = get_course_materials(common_page_data=common_page_data, get_video_content=False, get_pset_content=True)

    return render_to_response('videos/'+common_page_data['course_mode']+'/list.html', {'common_page_data': common_page_data, 'section_structures':section_structures, 'context':'problemset_list'}, context_instance=RequestContext(request))

