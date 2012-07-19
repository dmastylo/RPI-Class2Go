from django.shortcuts import render_to_response
from c2g.models import Course
from django.template import RequestContext

# Create your views here.
def list(request, course_prefix, course_suffix):
    course_handle = course_prefix + "-" + course_suffix
    course = Course.objects.get(handle=course_handle)
    psets = course.problemset_set.all().order_by('soft_deadline')
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
        numQuestions= len(pset.problem_set.all())
        numCompleted = len(course.problemactivity_set.filter(student=request.user).filter(problem_set=pset))
        if numQuestions == 0:
            progress = 0
        else:
            progress = 100.0*numCompleted/numQuestions
        dictionary = {"pset": pset, "numQuestions": numQuestions, "numCompleted": numCompleted, "progress": progress}
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
                               'pset': pset,
                               'pset_url':ps.path,
                              },
                              context_instance=RequestContext(request))
