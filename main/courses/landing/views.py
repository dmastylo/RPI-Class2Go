from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

def landing(request):
    """For normal servers, return our project landing page.  For maint servers,
    show our maintenance page."""

    context = RequestContext(request)
    maint_override = getattr(settings, 'MAINTENANCE_LANDING_PAGE', False)
    if maint_override:
        r = render_to_response('maint.html', context_instance=context)
    else:
        r = render_to_response('landing/landing.html', context_instance=context)
    return r
