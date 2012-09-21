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
        'cs144.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/cs144/Fall2012/preview'},
        'networking.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/networking/Fall2012/preview'}, 
        'matsci256.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/matsci256/Fall2012/preview'},
        'solar.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/solar/Fall2012/preview'},
        'security.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/security/Fall2012/preview'},
        'cs224n.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/cs224n/Fall2012'},        
        'nlp.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/nlp/Fall2012/preview'},
        'psych30.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/psych30/Fall2012/preview'}, 
        'perception.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/perception/Fall2012/preview'},
        'nano.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/nano/Fall2012/preview'},
        'crypto.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/crypto/Fall2012/preview'},
        'test.class.stanford.edu':{'host':'class.stanford.edu','prepend':'/test/Fall2012/preview'},        

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
            scheme='https' ###OVERRIDE hack
            return HttpResponseRedirect(scheme + '://' + self.redirect_dict[domain]['host'] + port_str + self.redirect_dict[domain]['prepend'] + request.get_full_path())
        return None #fallthrough
            
        
