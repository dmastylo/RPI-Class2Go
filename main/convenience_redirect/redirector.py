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
        'solar.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/solar/Fall2012'},
        'networking.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/networking/Fall2012'},        
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
                
        if port=='' :
            port_str= ''
        elif port=='80' and (not request.is_secure()):
            port_str= ''
        elif port=='443' and request.is_secure():
            port_str= ''
        else:
            port_str= ':' + port

        if (domain in self.redirect_dict):
            return HttpResponseRedirect(scheme + '://' + self.redirect_dict[domain]['host'] + port_str + self.redirect_dict[domain]['prepend'] + request.get_full_path())
        return None #fallthrough
            
        
