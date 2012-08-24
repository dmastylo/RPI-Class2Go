from django.utils.log import getLogger
from django.http import HttpResponse, HttpResponseRedirect

class convenience_redirector(object):
    """
    This is a middleware class that forwards request coming in on convenience domains to the appropriate place.
    For instance, www.class2go.stanford.edu -> class2go.stanford.edu.
    nlp.class2go.stanford.edu -> class2go.stanford.edu/nlp
    127.0.0.1:8000 -> localhost:8000
    """
    redirect_dict = {
        '127.0.0.1':'localhost'
        }

    def process_request(self, request):
        """
        Get the domain name from the host header (parse it apart from the port).
        Check it against the dict, then if there's a match do the redirect
        """
        if ('HTTP_HOST' not in request.META):
            return None #if we can't determine HOST we will proceed as usual
        (domain, sep, port) = request.META['HTTP_HOST'].partition(':')
        scheme = 'https' if request.is_secure() else 'http' 
        if (domain in self.redirect_dict):
            return HttpResponseRedirect(scheme + '://' + self.redirect_dict[domain] + ':' + port + request.get_full_path())
        return None #fallthrough
            
        
