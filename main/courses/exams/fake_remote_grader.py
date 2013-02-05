import urllib,urllib2
from StringIO import StringIO

from django.conf import settings

class fake_remote_grader_abstract(object):
    """
    Abstract base class for all fake remote graders.  Fake remote graders are 
    context managers that wrap test cases, ensuring that urllib gets correctly
    set up before the test, and then cleaned up afterward.

    Subclasses should override the fake_response(req) method that returns a
    response of the type urllib2.addinfourl().
    """

    def __init__(self, answer):
        self.answer = answer

    def __enter__(self):
        class FakeGraderHTTPHandler(urllib2.HTTPHandler):
            def http_open(inner_self, req):
                return self.fake_response(req)
        my_opener = urllib2.build_opener(FakeGraderHTTPHandler)
        urllib2.install_opener(my_opener)

    def __exit__(self, exc_type, exc_val, exc_tb):
        default_opener = urllib2.build_opener(urllib2.HTTPDefaultErrorHandler)
        urllib2.install_opener(default_opener)


class fake_remote_grader(fake_remote_grader_abstract):
    """
    Fake grader that will return 200 OK responses with the answer string that 
    this was instantiated with.  This is a context manager, so intended to be 
    used with a "with" statement, like so:

        ag = AutoGrader(xml)
        with fake_healthy_grader("all is well"):
            ag.grade("question", "answer")
    """

    def fake_response(self, req):
        grader_endpoint = getattr(settings, 'GRADER_ENDPOINT', 'localhost')
        if req.get_full_url() == grader_endpoint:
            resp = urllib2.addinfourl(StringIO(self.answer), "", req.get_full_url())
            resp.code = 200
            resp.msg = ""
            return resp
