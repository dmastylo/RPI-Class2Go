from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response, redirect, HttpResponseRedirect
from django.template import Context, loader
from c2g.models import Course, Video, VideoToExercise, Exercise

from c2g.models import Course, Video, VideoActivity, ProblemActivity
from courses.common_page_data import get_common_page_data
from courses.course_materials import get_course_materials
import datetime
from courses.videos.forms import *
from courses.forms import *
import gdata.youtube
import gdata.youtube.service
from django.db.models import Q

from django.template import RequestContext
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper

@auth_view_wrapper
def list(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    if 'id' in request.GET:
        #process Video model instance with this youtube id
        #and other stuff
        try:
            video = Video.objects.get(pk=request.GET['vid'])
        except Video.DoesNotExist:
            raise Http404

        video.url = request.GET['id']
        video.save()
        video.create_ready_instance()

    section_structures = get_course_materials(common_page_data=common_page_data, get_video_content=True)

    form = None
    if request.common_page_data['course_mode'] == "draft":
        form = LiveDateForm()

    return render_to_response('videos/'+common_page_data['course_mode']+'/list.html', {'common_page_data': common_page_data, 'section_structures':section_structures, 'context':'video_list', 'form': form}, context_instance=RequestContext(request))

@auth_view_wrapper
def view(request, course_prefix, course_suffix, slug):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    try:
        video = Video.objects.get(course=common_page_data['course'], slug=slug)
    except Video.DoesNotExist:
        raise Http404

    video_rec = request.user.videoactivity_set.filter(video=video)
    if video_rec:
        video_rec = video_rec[0]
    else:
        #note student field to be renamed to user, VideoActivity for all users now
        video_rec = VideoActivity(student=request.user, course=common_page_data['course'], video=video)
        video_rec.save()

    if video.mode == 'ready':
        draft_version = video.image
        video = draft_version

    return render_to_response('videos/view.html', {'common_page_data': common_page_data, 'video': video, 'video_rec':video_rec}, context_instance=RequestContext(request))

@auth_is_course_admin_view_wrapper
def edit(request, course_prefix, course_suffix, slug):
    common_page_data = request.common_page_data
    video = common_page_data['course'].video_set.all().get(slug=slug)
    form = S3UploadForm(course=common_page_data['course'], instance=video)

    return render(request, 'videos/edit.html',
            {'common_page_data': common_page_data,
             'slug': slug,
             'form': form,
             })

@auth_is_course_admin_view_wrapper
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


@auth_view_wrapper
def manage_exercises(request, course_prefix, course_suffix, video_slug):
    #Get all necessary information about the problemset
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    data = {'common_page_data': common_page_data}
    manage_form = ManageExercisesForm(initial={'course':common_page_data['course'].id})
    try:
        video = Video.objects.getByCourse(common_page_data['course']).get(slug=video_slug)
    except Video.DoesNotExist:
        raise Http404

    videoToExs = VideoToExercise.objects.filter(video__course=common_page_data['course'], is_deleted=False, video__slug=video_slug).order_by('video_time')
    used_exercises = []
    exercise_attempted = False
    if len(ProblemActivity.objects.filter(video_to_exercise__video=video.image)) > 0:
        exercise_attempted = True
    #Get the list of exercises currently in this problem set
    for videoToEx in videoToExs:
        used_exercises.append(videoToEx.exercise.id)
    #Get all the exercises in the course but not in this problem set to list in add from existing
    #Q objects allow queryset objects to be ORed together
    exercises = Exercise.objects.all().filter(Q(problemSet__course=common_page_data['course'])|Q(video__course=common_page_data['course'])).exclude(id__in=used_exercises).distinct()
    additional_form = AdditionalExercisesForm(initial={'course':common_page_data['course'].id}, used_exercises=exercises)
    reorder_form = ReorderExercisesForm(current_exercises=videoToExs)

    #Form processing action if form was submitted
    if request.method == 'POST':
        manage_form = ManageExercisesForm(request.POST, request.FILES)
        additional_form = AdditionalExercisesForm(request.POST, used_exercises=exercises)

        if manage_form.is_valid():
            
            #don't catch video DoesNotExist here because we want some tangible error to happen if
            #the video id changes in form submission, like emailing us
            video = Video.objects.get(id=request.POST['video_id'])
            file_content = request.FILES['file']
            file_name = file_content.name

            exercise = Exercise()
            exercise.handle = request.POST['course_prefix'] + '--' + request.POST['course_suffix']
            exercise.fileName = file_name
            exercise.file.save(file_name, file_content)
            exercise.save()

            video_time = request.POST['video_time']
            videoToEx = VideoToExercise(video=video, exercise=exercise, video_time=video_time, is_deleted=0, mode='draft')
            videoToEx.save()
            return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))

    #If form was not submitted then the form should be displayed or if there were errors the page needs to be rendered again
    data['manage_form'] = manage_form
    data['additional_form'] = additional_form
    data['reorder_form'] = reorder_form
    data['course_prefix'] = course_prefix
    data['course_suffix'] = course_suffix
    data['video'] = video
    data['videoToExs'] = videoToExs
    data['exercise_attempted'] = exercise_attempted
    data['exercises'] = exercises
    data['exercise_attempted'] = exercise_attempted
    return render_to_response('videos/manage_exercises.html', data, context_instance=RequestContext(request))

@auth_is_course_admin_view_wrapper
def add_exercise(request):
#    try:
#        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
#    except:
#        raise Http404

    #don't catch video DoesNotExist here because we want some tangible error to happen if
    #the video id changes in form submission, like emailing us
    video = Video.objects.get(id=request.POST['video_id'])

    video_time = request.POST['videotime']

    file_content = request.FILES['exercise']
    file_name = file_content.name

    exercise = Exercise()
    exercise.handle = request.POST['course_prefix'] + '--' + request.POST['course_suffix']
    exercise.fileName = file_name
    exercise.file.save(file_name, file_content)
    exercise.save()

    videoToEx = VideoToExercise(video=video, exercise=exercise, is_deleted=False, video_time=video_time)
    videoToEx.save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))

@auth_is_course_admin_view_wrapper
def add_existing_exercises(request):

    #don't catch video DoesNotExist here because we want some tangible error action to happen if
    #the video id changes in form submission, like mailing us
    video = Video.objects.get(id=request.POST['video_id'])

    exercise_ids = request.POST.getlist('exercise')
    exercises = Exercise.objects.filter(id__in=exercise_ids)
    for exercise in exercises:
        video_time = 0
        videoToEx = VideoToExercise(video=video, exercise=exercise, is_deleted=False, video_time=video_time, mode="draft")
        videoToEx.save()
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))


@auth_is_course_admin_view_wrapper
def save_exercises(request):
    #Function should only be accessed from submitting a form
    if request.method != 'POST':
        return redirect(request.META['HTTP_REFERER'])

    course_prefix = request.POST['course_prefix']
    course_suffix = request.POST['course_suffix']
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
 
    #don't catch video DoesNotExist here because we want some tangible error action to happen if
    #the video id changes in form submission, like mailing us
    video = Video.objects.get(id=request.POST['video_id'])

    action = request.POST['action']
    if action == 'Reset to Ready':
        video.revert()
        return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))
    else:
        videoToExs = VideoToExercise.objects.getByVideo(video)
        for videoToEx in videoToExs:
            videoToEx.video_time = request.POST[videoToEx.exercise.fileName]
            videoToEx.save()
        if action == 'Save and Set as Ready':
            video.commit()
        return HttpResponseRedirect(reverse('courses.videos.views.list', args=(request.POST['course_prefix'], request.POST['course_suffix'],)))

def delete_exercise(request):
    try:
        toDelete = VideoToExercise.objects.get(exercise__fileName=request.POST['exercise_file'], mode='draft', is_deleted=False)
        toDelete.delete()
        toDelete.save()

    except VideoToExercise.DoesNotExist:
        pass  #Do nothing if asked to delete non-existent video-exercise-relationship

    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], request.POST['video_slug'],)))

#enforce order by sorting by video_time
def get_video_exercises(request):
    import json
    try:
        video = Video.objects.get(id = request.GET['video_id'])
    except Video.DoesNotExist:
        raise Http404
    
    videoToExs = VideoToExercise.objects.select_related('exercise', 'video').filter(video=video, is_deleted=False).order_by('video_time')
    json_list = {}
    order = 0
    for videoToEx in videoToExs:
        json_list[str(videoToEx.video_time)]={}
        json_list[str(videoToEx.video_time)]['time']=videoToEx.video_time
        json_list[str(videoToEx.video_time)]['problemDiv']=videoToEx.exercise_id
        json_list[str(videoToEx.video_time)]['order']=order
        json_list[str(videoToEx.video_time)]['fileName']=videoToEx.exercise.fileName

        order=order+1

    json_string = json.dumps(json_list)
    return HttpResponse(json_string)

#enforce order by sorting by video_time
@auth_view_wrapper
def load_video_problem_set(request, course_prefix, course_suffix, video_id):

    vex_list = VideoToExercise.objects.select_related('exercise', 'video').filter(video_id=video_id, is_deleted=False).order_by('video_time')

    file_names = []
    for vex in vex_list:
        #Remove the .html from the end of the file name
        file_names.append(vex.exercise.fileName[:-5])
    # assessment type is hard-coded because all in-video exercises are formative
    return render_to_response('problemsets/load_problem_set.html',{'file_names': file_names, 'assessment_type': 'formative'},context_instance=RequestContext(request))
