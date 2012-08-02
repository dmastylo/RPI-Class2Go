from django.core.urlresolvers import reverse
from c2g.models import Course, ProblemActivity, ProblemSet, ContentSection, Exercise, ProblemSetToExercise
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from courses.common_page_data import get_common_page_data
from courses.course_materials import get_course_materials
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

# Filters all ProblemActivities by problem set and student. For each problem set, finds out how
# many questions there are and how many were completed to calculate progress on
# each problem set. Packages this information along with problem set
# information about deadlines into a dictionary and passes it to the template.

def list(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    section_structures = get_course_materials(common_page_data=common_page_data, get_video_content=False, get_pset_content=True)

    return render_to_response('problemsets/'+common_page_data['course_mode']+'/list.html', {'common_page_data': common_page_data, 'section_structures':section_structures}, context_instance=RequestContext(request))

def show(request, course_prefix, course_suffix, pset):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    ps = common_page_data['course'].problemset_set.get(slug=pset)
    #path = ProblemSet.objects(
    return render_to_response('problemsets/problemset.html',
                              {'common_page_data':common_page_data,
                               'pset': ps,
                               'pset_url':ps.path,
                              },
                              context_instance=RequestContext(request))

@csrf_exempt
def attempt(request, problemId):
    user = request.user
    pset = ProblemSet.objects.get(id=request.POST['pset_id'])
    exercise = pset.exercise_set.get(fileName=request.POST['exercise_filename'])
    problem = exercise.problem_set.get(slug=request.POST['slug'])
    problem_activity = ProblemActivity(student = user,
                                        problem = problem,
                                        exercise = exercise,
                                        complete = request.POST['complete'],
                                        attempt_content = request.POST['attempt_content'],
                                        count_hints = request.POST['count_hints'],
                                        time_taken = request.POST['time_taken'],
                                        attempt_number = request.POST['attempt_number'],
                                        problem_type = request.POST['problem_type'])

    problem_activity.save()
    if request.POST['complete'] == "1":
        return HttpResponse("complete")
    else:
        return HttpResponse("wrong")

def create_form(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    content_sections = common_page_data['course'].contentsection_set.all()
    return render_to_response('problemsets/create.html',
                            {'request': request,
                                'common_page_data': common_page_data,
                                'course_prefix': course_prefix,
                                'course_suffix': course_suffix,
                                'content_sections': content_sections
                            },
                            context_instance=RequestContext(request))

def create_action(request):
    course_handle = request.POST['course_prefix'] + "-" + request.POST['course_suffix']
    course = Course.objects.get(handle=course_handle, mode='staging')
    content_section = ContentSection.objects.get(id=request.POST['content_section'])
    pset = ProblemSet(course = course,
                    section = content_section,
                   slug = request.POST['slug'],
                   title = request.POST['title'],
                   description = request.POST['description'],
                   live_datetime = datetime.strptime(request.POST['live_date'],'%m/%d/%Y %H:%M'),
                   due_date = datetime.strptime(request.POST['due_date'],'%m/%d/%Y %H:%M'),
                   grace_period = datetime.strptime(request.POST['grace_period'],'%m/%d/%Y %H:%M'),
                   partial_credit_deadline = datetime.strptime(request.POST['partial_credit_deadline'],'%m/%d/%Y %H:%M'),
                   penalty_preference = request.POST['penalty_preference'],
                   late_penalty = request.POST['late_penalty'],
                   submissions_permitted = request.POST['submissions_permitted'],
                   resubmission_penalty = request.POST['resubmission_penalty'])
    pset.save()
    pset.create_production_instance()
    return HttpResponseRedirect(reverse('problemsets.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], pset,)))

def edit_form(request, course_prefix, course_suffix, pset_slug):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    content_sections = common_page_data['course'].contentsection_set.all()
    return render_to_response('problemsets/create.html',
                            {'request': request,
                                'common_page_data': common_page_data,
                                'course_prefix': course_prefix,
                                'course_suffix': course_suffix,
                                'content_sections': content_sections
                            },
                            context_instance=RequestContext(request))

def manage_exercises(request, course_prefix, course_suffix, pset_name):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404
    pset = ProblemSet.objects.get(course=common_page_data['course'], slug=pset_name)
    psetToExs = ProblemSetToExercise.objects.select_related('exercise', 'problemSet').filter(problemSet=pset).order_by('number')
    return render_to_response('problemsets/manage_exercises.html',
                            {'request': request,
                                'common_page_data': common_page_data,
                                'course_prefix': course_prefix,
                                'course_suffix': course_suffix,
                                'pset': pset,
                                'psetToExs': psetToExs
                            },
                            context_instance=RequestContext(request))

def add_exercise(request):
#    try:
#        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
#    except:
#        raise Http404

    pset = ProblemSet.objects.get(id=request.POST['pset_id'])
    exercise = Exercise(fileName=request.POST['exercise'])
    exercise.save()
    index = len(pset.exercise_set.all())
    psetToEx = ProblemSetToExercise(problemSet=pset, exercise=exercise, number=index)
    psetToEx.save()
    return HttpResponseRedirect(reverse('problemsets.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], pset,)))

def save_order(request):
    pset = ProblemSet.objects.get(id=request.POST['pset_id'])
    psetToEx = pset.problemsettoexercise_set.all().order_by('number')
    for n in range(0,len(psetToEx)):
        listName = "exercise_order[" + str(n) + "]"
        psetToEx[n].number = request.POST[listName]
        psetToEx[n].save()
    return HttpResponseRedirect(reverse('problemsets.views.manage_exercises', args=(request.POST['course_prefix'], request.POST['course_suffix'], pset,)))
