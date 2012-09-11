from c2g.models import Course
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect
import settings
import urlparse
from django.utils.functional import wraps


def redirects_use_http(response, request):
    '''This function changes all REDIRECT responses to http if they are https.
        Useful for downgrades after login/reg, etc.
    '''
    if isinstance(response, HttpResponseRedirect):
        return HttpResponseRedirect(urlparse.urljoin('http://'+request.get_host()+'/',response['Location']))
    return response



def upgrade_to_https_and_downgrade_upon_redirect(view):
    '''This decorator will make sure that the view, if accessed over http, will get upgrade to https
        Any subsequent redirects returned by this view will get downgraded
    '''
    @wraps (view)
    def inner(request, *args, **kw):
        #explicitly upgrading
        if (settings.INSTANCE == 'stage' or settings.INSTANCE == 'prod') and not request.is_secure():
            return redirect('https://'+request.get_host()+request.get_full_path())
        return redirects_use_http(view(request, *args, **kw),request)
    return inner
