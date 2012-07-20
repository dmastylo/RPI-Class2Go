from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from c2g.models import Course, ProblemSet
from django.template import RequestContext

# Create your views here.
def list(request, course_prefix, course_suffix):
    course_handle = course_prefix + "-" + course_suffix
    course = Course.objects.get(handle=course_handle)
    psets = course.problemset_set.all()
	
    f = open("C:/c2g_filestore/"+course_prefix+"-"+course_suffix+"/production/video_list.html","r")
    m_content = f.read();
    f.close()
	
    m_content = ListProcessor(raw_m_content, course, 'list')
    l_content = RestyleForLeftNavBar(m_content)
	
    return render_to_response('problemsets/list.html',
                              {'request': request,
                               'course_prefix': course_prefix,
                               'course_suffix': course_suffix,
							   'l_content': l_content,
							   'm_content': m_content,
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
                               'course_prefix': course_prefix,
                               'course_suffix': course_suffix,
                               'pset': pset,
                               'pset_url':ps.path,
                              }, 
                              context_instance=RequestContext(request))
