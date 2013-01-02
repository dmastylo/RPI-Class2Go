import re

from django.utils.log import getLogger
from django.http import HttpResponse, HttpResponseRedirect
from c2g.models import CurrentTermMap, Course

class convenience_redirector(object):
    """
    This is a middleware class that forwards request coming in on convenience domains to the appropriate place.
    For instance, 
    nlp.class2go.stanford.edu -> class2go.stanford.edu/nlp
    """
    #List of hostnames that will abort redirect if matched.  Need this because we have lots of
    #domain names are ancestors of each other, like class.stanford.edu, staging.class.stanford.edu, and
    #www.staging.class.stanford.edu
    domain_no_direct = ['class.stanford.edu','staging.class.stanford.edu','www.staging.class.stanford.edu','www.class.stanford.edu',\
                     'class2go.stanford.edu','staging.class2go.stanford.edu','www.staging.class2go.stanford.edu','www.class2go.stanford.edu']
    
    #List of regexes of domain names to match against. 
    regex_list = (
                    ('staging.class.stanford.edu',re.compile(r'^(?P<course_prefix>[a-zA-Z0-9_-]*)\.staging\.class\.stanford\.edu$', re.I)),
                    ('class.stanford.edu',re.compile(r'^(?P<course_prefix>[a-zA-Z0-9_-]*)\.class\.stanford\.edu$', re.I)),
                    ('staging.class2go.stanford.edu',re.compile(r'^(?P<course_prefix>[a-zA-Z0-9_-]*)\.staging\.class2go\.stanford\.edu$', re.I)),
                    ('class2go.stanford.edu',re.compile(r'^(?P<course_prefix>[a-zA-Z0-9_-]*)\.class2go\.stanford\.edu$', re.I)),
                  )
    
    
    curTerm = 'Fall2012'
    
    #factoring this out so we can unit test
    def get_prefix_and_host(self, domain):
        prefix = None
        for host,regex in self.regex_list:
            matchobj = regex.match(domain)
            if matchobj:
                prefix = matchobj.groups()[0]
                break
        return prefix,host

    def get_prefix_suffix_from_path(self, path):
        path_regex = re.compile(r'^/(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/?', re.I)
        matchobj = path_regex.match(path)
        if not matchobj:
            return None
        return (matchobj.groups()[0], matchobj.groups()[1])


    def process_request(self, request):
        """
        Get the domain name from the host header (parse it apart from the port).
        Check it against the regex, then if there's a match do the redirect
        """
        if ('HTTP_HOST' not in request.META):
            return None #if we can't determine HOST we will do no redirect
        
        (domain, sep, port) = request.META['HTTP_HOST'].partition(':')
        scheme = 'https' if request.is_secure() else 'http'

        if domain in self.domain_no_direct:
            #Check PATH to see if we need to redirect to the right codebase
            req_path = request.get_full_path()
            pathobj = self.get_prefix_suffix_from_path(req_path)
            if pathobj:
                (path_prefix, path_suffix) = pathobj
                if not Course.objects.filter(handle=path_prefix+'--'+path_suffix).exists(): #only redirect class-related URLs
                    return None
                if path_suffix == 'Fall2012': #send requests to Fall2012 classes under the new codebase back to the old codebase
                    http_host=re.sub(r'class2go\.', 'class.', request.META['HTTP_HOST'], flags=re.I)
                else:  #send everyone else to the new codebase
                    http_host=re.sub(r'class\.', 'class2go.', request.META['HTTP_HOST'], flags=re.I)
            
                if http_host == request.META['HTTP_HOST']: #prevent redirect loop.  Don't redirect if there's no reason to
                    return None
                return HttpResponseRedirect(scheme + '://' + http_host + request.get_full_path())
            else:
                return None
        
        prefix,host = self.get_prefix_and_host(domain) #now get the class prefix, 'networking, for example
        if not prefix:
            return None #if there was no matching convenience name, don't redirect
            
        if port=='' :
            port_str= ''
        elif port=='80' and (not request.is_secure()):
            port_str= ''
        elif port=='443' and request.is_secure():
            port_str= ''
        else:
            port_str= ':' + port

        #lookup suffix from database -- decided this is okay because no DB access will happen if the access
        #uses the normal URLs (e.g. class.stanford.edu), which we expect to be the common case
                
                
        try:
            suffix = CurrentTermMap.objects.get(course_prefix=prefix).course_suffix
        except CurrentTermMap.DoesNotExist:
            suffix = self.curTerm # Use this as default fallback

        #Do redirects at the convenience domain name level
        if suffix == 'Fall2012': #send requests to Fall2012 classes under the new codebase back to the old codebase
            host=re.sub(r'class2go\.', 'class.', host, flags=re.I)
        else:  #send everyone else to the new codebase
            host=re.sub(r'class\.', 'class2go.', host, flags=re.I)


        return HttpResponseRedirect(scheme + '://' + host + port_str + '/' + prefix + '/' + suffix + request.get_full_path())
        
            
        
