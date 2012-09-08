from django.contrib.auth.models import User
from c2g.models import UserProfile

import logging
logger = logging.getLogger(__name__)

class user_profiling(object):
    """
    Middleware to keep track of the stuff about the user that we want to keep track of.  
    The results end up in the UserProfile model.
    """
    def process_view (self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
                try:
                    profile.client_ip = request.META['X-FORWARDED-FOR']
                except KeyError:
                    try:
                        profile.client_ip = request.META['REMOTE_ADDR']
                    except KeyError:
                        pass

                try:
                    profile.referrer = request.META['HTTP_REFERRER']
                except KeyError:
                    pass

                try:
                    profile.user_agent = request.META['HTTP_USER_AGENT']
                except KeyError:
                    pass
                
                try:
                    profile.accept_language = request.META['HTTP_ACCEPT_LANGUAGE']
                except KeyError:
                    pass

                if profile.client_ip_first is None:
                    profile.client_ip_first = profile.client_ip
                    profile.user_agent_first = profile.user_agent
                    profile.referrer_first = profile.referrer
                    profile.accept_language_first = profile.accept_language

                profile.save()

            except UserProfile.DoesNotExist:
                # Some users might not have a user profile object
                # that's OK, don't do any tracking for those
                pass

        
