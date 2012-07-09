from django.http import HttpResponse
from django.shortcuts import render_to_response
from c2g.models import Course, ProblemSet
from django.template import RequestContext

# Create your views here.
def list(request, course_prefix, course_suffix):
    psets = ProblemSet.objects.all()
    return render_to_response('problemsets/list.html',
                              {'request': request,
                               'course_prefix': course_prefix,
                               'course_suffix': course_suffix,
                               'psets': psets,
                              },
                              context_instance=RequestContext(request))

def show(request, course_prefix, course_suffix, pset ):
    course_handle = course_prefix + "-" + course_suffix
    course = Course.objects.get(handle=course_handle)
    ps = course.problemset_set.get(title=pset)
    #path = ProblemSet.objects(
    return render_to_response('problemsets/problemset.html', 
                              {'request': request, 
                               'course_handle': course_handle,
                               'pset': pset,
                               'pset_url':ps.path,
                              }, 
                              context_instance=RequestContext(request))
