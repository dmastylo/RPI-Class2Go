import socket, sys, traceback, datetime, re
import settings
from django.core.mail import send_mail
from django import http
from django.shortcuts import Http404, render
from django.utils.log import getLogger

logger = getLogger('django.request')

mailto_list = getattr(settings, 'ERROR_SNIPPET_EMAILS', [])
from_addr = getattr(settings, 'DEFAULT_FROM_EMAIL', "admin@localhost")

class error_ping(object):
    """
    This is a middleware class that sends short email snippets per uncaught exception
    """
    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return None
        username = request.user.username if request.user.is_authenticated() else "Anonymous"
        datestring = datetime.datetime.isoformat(datetime.datetime.now())
        user_agent = request.META.get('HTTP_USER_AGENT', 'NO USER AGENT FOUND')
        exc_info = sys.exc_info()
        (type, value, tb) = exc_info
        (path, lineno, exc, text) = traceback.extract_tb(tb)[-1]
        email_subj = "%s on %s" % (repr(exception), repr(socket.gethostname()))
        email_subj = re.sub(r'\n','',email_subj)
        email_msg = "User: %s\nTime: %s\nUser-agent: %s\nFile path %s:%d\nLine text: %s\n" % (username, datestring, user_agent, path, lineno,  text)
        send_mail(email_subj, email_msg, from_addr, mailto_list)
        del tb
    
        u = request.user
        if not settings.DEBUG and u.is_authenticated() and (u.userprofile.is_instructor_list() or u.userprofile.is_tas_list() or u.userprofile.is_readonly_tas_list()):
            #if on production
            #want to return a different 500 msg for course staff.
            #but because we return a response instead of None, django's
            #default error handling (including logging and stacktrace email)
            #won't be invoked, so we have to do that manually.
            
            #cribbing from django/core/handlers/base.py
            logger.error('Internal Server Error: %s', request.path,
                exc_info=exc_info,
                extra={
                'status_code': 500,
                'request': request
                }
            )
            
            site = getattr(settings, 'SITE_NAME_SHORT')
            return render(request, 'sites/%s/500_staff.html' % site)
                
        return None
