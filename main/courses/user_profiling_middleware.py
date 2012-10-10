
from django.contrib.auth.models import User
from django.conf import settings
from c2g.models import UserProfile

from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)


class user_profiling(object):
    """
    Middleware to keep track of useful stuff about the user.  Only update once 
    per day (overrideable).  The results end up in the UserProfile model.

    Note that we use the last_update timestamp for this, which will be updated
    by *anything* writing to the UserProfile model.  So if there is something
    else writing to this table frequently then we will stop updating this client
    information.  Fix for this would be to track a separate timestamp for client
    info tracking time -- that feels like overkill for now.
    """
    def process_view (self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()

                # don't update client data too frequently, bad for performance
                # by defaut, once per day
                resolution = getattr(settings, "PROFILE_UPDATE_RESOLUTION", 86400)
                delta = datetime.now()-profile.last_updated
                diff = timedelta(seconds=resolution)
                if delta < diff:
                    return

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

