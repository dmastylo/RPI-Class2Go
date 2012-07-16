from django.shortcuts import render_to_response
from c2g.models import Course, ProblemSet, ProblemActivity
from django.template import RequestContext

# Create your views here.
def list(request, course_prefix, course_suffix):
    course_handle = course_prefix + "-" + course_suffix
    course = Course.objects.get(handle=course_handle)
    psets = course.problemset_set.all()
    pset_and_progress = {}

    for pset in psets:
        completed = course.problemactivity_set.filter(student=request.user).filter(problem_set=pset)
        numCompleted = len(completed)
        progress = 100.0*numCompleted/pset.question_count
        pset_and_progress[pset] = progress

    return render_to_response('problemsets/list.html',
                              {'request': request,
                               'course_prefix': course_prefix,
                               'course_suffix': course_suffix,
                               'psets': psets,
                               'pset_and_progress': pset_and_progress,
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
                               'pset': pset,
                               'pset_url':ps.path,
                              },
                              context_instance=RequestContext(request))
