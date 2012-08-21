from courses.common_page_data import get_common_page_data
from django.http import Http404

import logging
logger = logging.getLogger(__name__)

class common_data(object):
    """
    This is a middleware class that eagerly retrieves page data that might be common to most requests.  It is 
    basically a wrapper around Sherif's implementation of common_page_data.  The data is stored as a field of 
    request.
    """
    def process_view (self, request, view_func, view_args, view_kwargs):
        if (('course_prefix' not in view_kwargs) or 
            ('course_suffix' not in view_kwargs)):
            return None # Bail out in this case since we can't find the course
        try:
            request.common_page_data=get_common_page_data(request, view_kwargs['course_prefix'], 
                                                      view_kwargs['course_suffix'])
            return None
        except:
            raise Http404