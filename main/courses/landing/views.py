
from django.shortcuts import render_to_response
from django.template import RequestContext
from c2g.models import Course

def landing(request):
    context = RequestContext(request)

    course_list = Course.objects.filter(mode='ready')
    
    
    return render_to_response('landing/landing.html', {'course_list':course_list}, context_instance=context)

