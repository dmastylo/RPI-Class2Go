
from django.shortcuts import render_to_response
from django.template import RequestContext

def landing(request):
    context = RequestContext(request)
    return render_to_response('landing/landing.html', context_instance=context)

