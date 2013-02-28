import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response, redirect, HttpResponseRedirect
from django.template import RequestContext

from c2g.models import ContentGroup, ContentSection, Exam, ExamRecord, Exercise, PageVisitLog, ProblemActivity, Video, VideoActivity, VideoToExercise, videos_in_exam_metadata
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper
from courses.common_page_data import get_common_page_data
from courses.course_materials import get_course_materials
from courses.videos.forms import *
from courses.forms import *


@auth_view_wrapper
def list(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    request.session['headless'] = request.GET.get('headless')

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

    common_page_data = request.common_page_data
    
    try:
        #getByCourse takes care of checking for draft vs live, is_deleted and live times
        video = Video.objects.getByCourse(course=common_page_data['course']).get(slug=slug)
    except Video.DoesNotExist:
        raise Http404
    
    if not common_page_data['is_course_admin']:
        visit_log = PageVisitLog(
            course = common_page_data['ready_course'],
            user = request.user,
            page_type= 'video',
            object_id = str(video.id),
        )
        visit_log.save()

    if not 'video_quiz_mode' in request.session:
        #Default to include quizzes in viewing videos
        request.session['video_quiz_mode'] = "quizzes included"

    videos = Video.objects.getByCourse(course=common_page_data['course'])
    #Get index of current video
    cur_index = None #just code safety
    for index, item in enumerate(videos):
        if item == video:
            cur_index = index
            break

    ready_section = video.section
    if ready_section and ready_section.mode == "draft":
        ready_section = ready_section.image

    #code safety
    next_slug = None
    prev_slug = None

    if cur_index is not None:
        if cur_index > 0:
            prev_slug = videos[cur_index-1].slug
        else:
            prev_slug = None
        if cur_index < videos.count() - 1:
            next_slug = videos[cur_index+1].slug
        else:
            next_slug = None

    video_rec = request.user.videoactivity_set.filter(video=video)
    if video_rec:
        video_rec = video_rec[0]
    else:
        #note student field to be renamed to user, VideoActivity for all users now
        video_rec = VideoActivity(student=request.user, course=common_page_data['course'], video=video)
        video_rec.save()
        
    course = common_page_data['course']

    key = ('video', video.id)
    l1items, l2items = get_contentgroup_data(course=course)
    downloadable_content = get_children(key, l1items, l2items)

    if video.exam:
        try:
            exam = video.exam
            video_obj = videos_in_exam_metadata(exam.xml_metadata, times_for_video_slug=video.slug)
            question_times = video_obj['question_times']

        except Exam.DoesNotExist:
            raise Http404
    else:
        sections = ContentSection.objects.getByCourse(course) 
        section = sections[0]
        # create fake exam as exam template (which is what displays all videos) needs exam data to function
        # correctly (TODO: Refactor this)
        exam = Exam(course=course, slug=slug, title=video.title, description="Empty Exam", html_content="", xml_metadata="", due_date='', assessment_type="survey", mode="draft", total_score=0, grade_single=0, grace_period='', partial_credit_deadline='', late_penalty=0, submissions_permitted=0, resubmission_penalty=0, exam_type="survey", autograde=0, display_single=0, invideo=1, section=section,)
        exam.live_datetime = video.live_datetime    # needed so video shows up
        question_times = ""

    return render_to_response('exams/view_exam.html', 
                              {
                               'common_page_data':    common_page_data, 
                               'video':               video,
                               'ready_section':       ready_section,
                               'video_rec':           video_rec, 
                               'prev_slug':           prev_slug, 
                               'next_slug':           next_slug, 
                               'downloadable_content':downloadable_content,
                               'json_pre_pop':"{}",
                               'scores':"{}",
                               'editable':True,
                               'single_question':exam.display_single,
                               'videotest':exam.invideo,
                               'question_times':json.dumps(question_times),
                               'allow_submit':True,
                               'children': downloadable_content,
                               'exam':exam
                              },
                              context_instance=RequestContext(request))



@auth_is_course_admin_view_wrapper
def edit(request, course_prefix, course_suffix, slug):
    common_page_data = request.common_page_data
    video = common_page_data['course'].video_set.all().get(slug=slug)
    form = S3UploadForm(course=common_page_data['course'], instance=video)
    try:
        psets = Exam.objects.filter(course_id=common_page_data['course'].id, invideo=True, is_deleted=0)
    except:
        raise Http404 

    return render(request, 'videos/edit.html',
            {'common_page_data': common_page_data,
             'slug': slug,
             'form': form,
             'video': video,
             'psets': psets,
             })

@auth_is_course_admin_view_wrapper
def upload(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    data = {'common_page_data': common_page_data}

    try:
        exam = Exam.objects.filter(course_id=common_page_data['course'].id, invideo=True)
    except:
        raise Http404 

    form = S3UploadForm(course=common_page_data['course'])
    data['form'] = form
    data['psets'] = exam 

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
    if ProblemActivity.objects.filter(video_to_exercise__video=video.image).exists():
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
            video_time = request.POST['video_time']
            file_content = request.FILES['file']
            file_name = file_content.name

            exercises = Exercise.objects.filter(handle=course_prefix+"--"+course_suffix,is_deleted=0)
            exercise_exists = False
            for exercise in exercises:
                if exercise.fileName == file_name:
                    #We don't wipe out all problem activites associated with this
                    #existing exercise, but if it's a nontrivial overwrite, should we?
                    exercise.file = file_content
                    exercise.save()
                    exercise_exists = True

                    #If exercise already in video, don't need to create new videoToEx, just update video_time
                    #If exercise already in video but deleted, undelete
                    #Otherwise create new videoToEx
                    queryVideoToEx = VideoToExercise.objects.filter(video=video, exercise=exercise, mode='draft').order_by('-id')
                    if queryVideoToEx.exists():
                        existingVideoToEx = queryVideoToEx[0]
                        if existingVideoToEx.is_deleted == 1:
                            existingVideoToEx.is_deleted = 0
                            existingVideoToEx.video_time = video_time
                            existingVideoToEx.save()
                        else:
                            existingVideoToEx.video_time = video_time
                            existingVideoToEx.save()
                    else:
                        videoToEx = VideoToExercise(video=video, exercise=exercise, video_time=video_time, is_deleted=0, mode='draft')
                        videoToEx.save()
                    break

            if not exercise_exists:
                exercise = Exercise()
                exercise.handle = request.POST['course_prefix'] + '--' + request.POST['course_suffix']
                exercise.fileName = file_name
                exercise.file.save(file_name, file_content)
                exercise.save()

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
        #if this exercise has been deleted previously then just un-delete it
        videoToExs = VideoToExercise.objects.filter(video=video, exercise_id=exercise.id, mode = 'draft', is_deleted=1).order_by('-id')
        if videoToExs.exists():
            videoToEx = videoToExs[0]
            videoToEx.is_deleted = 0
            videoToEx.video_time = 0
            videoToEx.save()
        #else create a new one
        else:
            videoToEx = VideoToExercise(video=video, exercise=exercise, is_deleted=0, video_time=0, mode='draft')
            videoToEx.save()       
        
    return HttpResponseRedirect(reverse('courses.videos.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], video.slug,)))


@auth_is_course_admin_view_wrapper
def save_exercises(request):
    #Function should only be accessed from submitting a form
    if request.method != 'POST':
        return redirect(request.META['HTTP_REFERER'])

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
        handle = request.POST['course_prefix']+'--'+request.POST['course_suffix']
        toDelete = VideoToExercise.objects.get(exercise__handle=handle,exercise__fileName=request.POST['exercise_file'], mode='draft', is_deleted=False, video__slug=request.POST['video_slug'])
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

####
# Extra utility methods not used by get_course_materials 
####
def get_contentgroup_data(course):
    """Old method of memoizing ContentGroup."""
    # TODO: figure out how to remove this and all its children
    l1_items = {}
    l2_items = {}
    for cgtype, cgtid, cgref, target, level, display in [__get_group_item_data(x, selfref=True) for x in 
                                                            ContentGroup.objects.getByCourse(course=course)]:
        if not target.is_live() or target.is_deleted:
            continue
        if level == 2:
            l2_items[(cgtype, cgtid)] = (cgref, target, level, display)
        else:
            l1_items[(cgtype, cgtid)] = cgref.group_id
    return l1_items, l2_items

def __get_group_item_data(group_item, selfref=False):
    ctype   = group_item.get_content_type()
    level   = group_item.level
    display = group_item.display_style or 'list'
    target  = getattr(group_item, ctype)
    cgid    = target.id
    if not selfref:
        return ctype, cgid, target, level, display
    return ctype, cgid, group_item, target, level, display

def get_children(key, level1_items, level2_items, user=None):

    def type_sorter(ci1, ci2):
        ci1_type = ci1['type']
        ci2_type = ci2['type']
        ci1_title = ci1['title']
        ci2_title = ci2['title']
        if ci1_type < ci2_type:
            return -1
        elif ci1_type > ci2_type:
            return +1
        else:
            # equal types, go by title
            if ci1_title < ci2_title:
                return -1
            elif ci1_title > ci2_title:
                return +1
            else:
                return 0

    def name_sorter(ci1, ci2):
        ci1_name = ci1['name']
        ci2_name = ci2['name']
        ci1_ext = ci1['ext']
        ci2_ext = ci2['ext']
        if ci1_name and ci2_name:
            if ci1_ext < ci2_ext:
                return -1
            elif ci1_ext > ci2_ext:
                return +1
            else:
                # equal extensions, go by filename
                if ci1_name < ci2_name:
                    return -1
                elif ci1_name > ci2_name:
                    return +1
                else:
                    return 0
        else:
            return 0

    children = []
    if level1_items.has_key(key):
        group_id = level1_items[key]
        children.extend([__augment_child_data(k, v, user) for k,v in level2_items.items() if v[0].group_id == group_id])
        children = sorted(sorted(children, type_sorter), name_sorter)
    return children

def __augment_child_data(key, value, user=None):
    class NoFile():
        name = ''
    cgtype = key[0]
    ref    = value[1]
    tmp_f  = getattr(ref, 'file', NoFile())
    name   = tmp_f.name.split('/').pop()
    ext    = name.split('.').pop().lower()

    #              target             target        this entry    target ref  
    child_data = {'type': cgtype, 'id': key[1], 'self': value[0], 'ref': ref, 'display': value[3], 'ext': ext,
                  'name': name, 'title': ref.title, 'url': ref.get_url(), 'index': ref.index, 'children': None, }
    child_data[cgtype] = ref      # TODO: set 'exam':exam - remove after making templates use 'ref'
    if cgtype == "exam" and user: # TODO: per-type special cases belong somewhere else?
        child_data['records'] = ExamRecord.objects.filter(course=ref.course, student=user, complete=True, exam=ref)
    return child_data
    
