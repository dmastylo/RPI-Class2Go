from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

def landing(request):
    """For normal servers, return our project landing page.  For maint servers,
    show our maintenance page.  Hiring shows a little banner stripe."""
    hiring=True
    context = RequestContext(request)
    maint_override = getattr(settings, 'MAINTENANCE_LANDING_PAGE', False)
    if maint_override:
        r = render_to_response('maint.html', {'hiring': hiring}, context_instance=context)
    else:
        r = render_to_response('landing/landing.html', {'hiring': hiring}, context_instance=context)
    return r

def hiring(request):
    context = RequestContext(request)
    return render_to_response('landing/hiring.html', context_instance=context)
