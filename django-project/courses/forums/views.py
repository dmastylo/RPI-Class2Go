from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
import httplib 
from OAuthSimple import OAuthSimple
from urlparse import urlparse
import urllib 

# won't be needed once we remove the dash from the directory name (soon)
secrets_file = __import__('django-project.database', globals(), locals(), ['PIAZZA_CONSUMER_KEY', 'PIAZZA_OAUTH_SECRET'], -1)


def admin(request, course_prefix, course_suffix):
	return render_to_response('forums/admin.html', 
            {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, 
            context_instance=RequestContext(request))


def view(request, course_prefix, course_suffix):
    # settings for OAuth
    url_full='https://piazza.com/basic_lti'
    url_parsed = urlparse(url_full)
    signatures = {'consumer_key': secrets_file.PIAZZA_CONSUMER_KEY, 
            'shared_secret': secrets_file.PIAZZA_OAUTH_SECRET}
    
    # TODO: make dynamic
    lti_params = {
          "lti_message_type": "basic-lti-launch-request",
          "lti_version": "LTI-1p0",
          "resource_link_id": "120988f929-274612",
          "resource_link_title": "Weekly Blog",
          "resource_link_description": "A weekly blog.",
          "user_id": "8321264",
          "lis_person_name_full": "Jane Q. Public",
          "lis_person_contact_email_primary": "sef@cs.stanford.edu",
          "lis_person_sourcedid": "school.edu:user",
          "tool_consumer_instance_description": "University of School (LMSng)",
          "launch_presentation_return_url": "http://example.com/lti_return",
          "ext_lti_message_type": "extension-lti-launch",
          "ext_submit": "Press to Launch",
          "roles": 'Instructor',
          "context_label": "LTI 101",
          "context_id": "47264",
          "context_title": "foo",
          "context_type": "bar",
          "oauth_callback": "about:blank",
    }

    oauthsimple = OAuthSimple()
    sign = oauthsimple.sign({ 'path': url_full, 'action': 'POST',
        'parameters': lti_params, 'signatures': signatures})
    signed_encoded_body = urllib.urlencode(sign['parameters']);

    headers = {'Content-type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'max-age=0'};

    if url_parsed.scheme == 'https':
        conn = httplib.HTTPSConnection(url_parsed.netloc)
    else:
        conn = httplib.HTTPConnection(url_parsed.netloc)
    conn.request("POST", url_parsed.path, signed_encoded_body, headers)
    response = conn.getresponse()

    # for now just dump out a bunch of ugly debugging info.  
    # header_pretty = '<br>'.join('%s: %s' % (key, value) for (key, value) in headers.items())
    # params_pretty = '<br>'.join('%s = %s' % (key, value) for (key, value) in sign['parameters'].items())
    # return HttpResponse("HOST=" + url_parsed.netloc
            # + "<br>PATH=" + url_parsed.path
            # + "<hr>SBS=" + sign['sbs']
            # + "<hr>HEADERS<br>" + header_pretty
            # + "<hr>BODY<br>" + params_pretty
            # + "<hr>RESPONSE=" + str(response.status) + " " + response.reason
            # + "<hr>OUTPUT<br>" + response.read()
            # )

    # TODO: put in iframe
    return HttpResponse(response.read())
