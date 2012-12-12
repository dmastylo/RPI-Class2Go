import socket, sys, traceback, datetime, re
from django.core.mail import send_mail
from django.shortcuts import Http404
import settings
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
        (type, value, tb) = sys.exc_info()
        (path, lineno, exc, text) = traceback.extract_tb(tb)[-1]
        email_subj = "%s on %s" % (repr(exception), repr(socket.gethostname()))
        email_subj = re.sub(r'\n','',email_subj)
        email_msg = "User: %s\nTime: %s\nUser-agent: %s\nFile path %s:%d\nLine text: %s\n" % (username, datestring, user_agent, path, lineno,  text)
        send_mail(email_subj, email_msg, from_addr, mailto_list)
        del tb
        return None
