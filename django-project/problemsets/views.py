from django.http import HttpResponse
from django.shortcuts import render_to_response
from c2g.models import Course, ProblemSet
from django.template import RequestContext

# Create your views here.
def show(request, course_prefix, course_suffix, pset ):
    course_name = course_prefix + "-" + course_suffix
    course = Course.objects.get(title=course_name)
    ps = course.problemset_set.get(title=pset)
    #path = ProblemSet.objects(
    return render_to_response('problemsets/problemset.html', 
                              {'request': request, 
                               'course_name': course_name,
                               'pset': pset,
                               'pset_url':ps.path,
                              }, 
                              context_instance=RequestContext(request))
