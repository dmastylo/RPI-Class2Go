from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from c2g.models import Course
from django.db.models import Q

def landing(request):
    """For normal servers, return our project landing page.  For maint servers,
    show our maintenance page."""

    context = RequestContext(request)

    """ if logged in show institution courses if appropriate 
        other rules: superuser - sees all
                     staff - sees all from institution?
    """
    

    if not request.user.is_authenticated():
        course_list = Course.objects.filter(mode='ready', institution_only = 0)
    else:
        course_list = Course.objects.filter(Q(mode='ready', institution_only = 0) | Q(mode='ready', institution__id__in=request.user.get_profile().institutions.all()))
        
    maint_override = getattr(settings, 'MAINTENANCE_LANDING_PAGE', False)
    if maint_override:
        r = render_to_response('maint.html', context_instance=context)
    else:
        r = render_to_response('landing/landing.html', {'course_list':course_list, 'display_login': request.GET.__contains__('login')}, context_instance=context)
    return r
    
