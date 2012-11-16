from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from c2g.models import Course

def landing(request):
    """For normal servers, return our project landing page.  For maint servers,
    show our maintenance page."""

    context = RequestContext(request)

    course_list = Course.objects.filter(mode='ready')

    maint_override = getattr(settings, 'MAINTENANCE_LANDING_PAGE', False)
    if maint_override:
        r = render_to_response('maint.html', context_instance=context)
    else:
        r = render_to_response('landing/landing.html', {'course_list':course_list}, context_instance=context)
    return r
    
