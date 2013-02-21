import urllib,urllib2
from StringIO import StringIO

from django.conf import settings
from django.core.cache import get_cache

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
        # clear out the grader cache every time we fake out the grader
        gradercache = get_cache('grader_store')
        gradercache.clear()

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
            g = ag.grade("question", "answer")
    """

    def fake_response(self, req):
        grader_endpoint = getattr(settings, 'GRADER_ENDPOINT', 'localhost')
        if req.get_full_url() == grader_endpoint:
            resp = urllib2.addinfourl(StringIO(self.answer), "", req.get_full_url())
            resp.code = 200
            resp.msg = "OK"
            return resp


class fake_remote_grader_fails(fake_remote_grader):
    """
    Fake remote grader that will fail after either a number of 
    successes, or will fail some number of times before 
    succeeding. Inherits from fake_remote_grader, instead of the 
    abstract parent, so it can use the child's happy-path responder.
    """

    def __init__(self, answer, fail_after=0, fail_for=0):
        self.failures = 0
        self.successes = 0
        self.fail_after = fail_after
        self.fail_for = fail_for
        super(fake_remote_grader_fails, self).__init__(answer)

    def fake_response(self, req):
        grader_endpoint = getattr(settings, 'GRADER_ENDPOINT', 'localhost')
        if req.get_full_url() == grader_endpoint:
            if (self.fail_for > 0 and self.failures < self.fail_for) \
                    or (self.fail_after > 0 and self.successes >= self.fail_after):
                self.failures += 1
                resp = urllib2.addinfourl(StringIO(""), "", req.get_full_url())
                resp.code = 500
                resp.msg = "Server Error"
            else:
                self.successes += 1
                resp = super(fake_remote_grader_fails, self).fake_response(req)
            return resp


class fake_remote_grader_garbage(fake_remote_grader_abstract):
    """
    Fake grader that will return connection junk that shouldn't be parsable
    as a HTTP response.
    """
    def fake_response(self, req):
        grader_endpoint = getattr(settings, 'GRADER_ENDPOINT', 'localhost')
        if req.get_full_url() == grader_endpoint:
            return "garbage_response"


