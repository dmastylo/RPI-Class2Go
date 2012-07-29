from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from c2g.models import Course, ProblemActivity, ProblemSet
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

# Filters all ProblemActivities by problem set and student. For each problem set, finds out how
# many questions there are and how many were completed to calculate progress on
# each problem set. Packages this information along with problem set
# information about deadlines into a dictionary and passes it to the template.

def list(request, course_prefix, course_suffix):
    course_handle = course_prefix + "-" + course_suffix
    course = Course.objects.get(handle=course_handle)
    psets = course.problemset_set.all().order_by('due_date')
    package = []

    if not request.user.is_authenticated():
        return render_to_response('problemsets/list.html',
                                {'request': request,
                                'course_prefix': course_prefix,
                                'course_suffix': course_suffix,
                                'course': course,
                                },
                                context_instance=RequestContext(request))

    for pset in psets:
        exercises = pset.exercise_set.all()
        numQuestions = len(exercises)
        #Starting values are total questions and will be subtracted from
        numCompleted = numQuestions
        numCorrect = numQuestions
        for exercise in exercises:
            attempts = exercise.problemactivity_set.filter(student = request.user).exclude(attempt_content="hint")

            #Counts the completed problems by subtracting all without a student activity recorded for it
            if len(attempts) == 0:
                numCompleted -= 1

            #Add one to the number of correctly answered questions if the first attempt is correct
            attempts.filter(attempt_number = 1)
            for attempt in attempts:
                if attempt.complete == 0:
                    numCorrect -= 1
                    break

        #Divide by zero safety check
        if numQuestions == 0:
            progress = 0
        else:
            progress = 100.0*numCompleted/numQuestions

        dictionary = {"pset": pset, "numQuestions": numQuestions, "numCompleted": numCompleted, "progress": progress, "numCorrect": numCorrect}
        package.append(dictionary)

    return render_to_response('problemsets/list.html',
                              {'request': request,
                               'course_prefix': course_prefix,
                               'course_suffix': course_suffix,
                                'course': course,
                               'package': package,
                              },
                              context_instance=RequestContext(request))

def show(request, course_prefix, course_suffix, pset ):
    course_handle = course_prefix + "-" + course_suffix
    course = Course.objects.get(handle=course_handle)
    ps = course.problemset_set.get(title=pset)
    #path = ProblemSet.objects(
    return render_to_response('problemsets/problemset.html',
                              {'request': request,
                               'course_prefix': course_prefix,
                               'course_suffix': course_suffix,
                                'course': course,
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
    return render_to_response('problemsets/create.html',
                            {'request': request,
                                'course_prefix': course_prefix,
                                'course_suffix': course_suffix,
                            },
                            context_instance=RequestContext(request))

def create_action(request):
    course_handle = request.POST['course_prefix'] + "-" + request.POST['course_suffix']
    course = Course.objects.get(handle=course_handle)
    randomize = False
    if request.POST['randomize'] == 'on':
        randomize = True
    pset = ProblemSet(course = course,
                   title = request.POST['title'],
                   name = request.POST['name'],
                   description = request.POST['description'],
                   live_date = request.POST['live_date'],
                   due_date = request.POST['due_date'],
                   grace_period = request.POST['grace_period'],
                   partial_credit_deadline = request.POST['partial_credit_deadline'],
                   penalty_preference = request.POST['penalty_preference'],
                   late_penalty = request.POST['late_penalty'],
                   submissions_permitted = request.POST['submissions_permitted'],
                   resubmission_penalty = request.POST['resubmission_penalty'],
                   randomize = randomize)
    pset.save()
    return HttpResponseRedirect(reverse('problemsets.views.list', args=(request.POST['course_prefix'], request.POST['course_suffix'],)))




