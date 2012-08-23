from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from courses.common_page_data import get_common_page_data
    
from courses.forums.forms import PiazzaAuthForm

import httplib 
from OAuthSimple import OAuthSimple
from urlparse import urlparse
import urllib 


# won't be needed once we remove the dash from the directory name
# see https://github.com/Stanford-Online/class2go/issues/125
database_dot_py_config = __import__('django-project.database', globals(), locals(), 
        ['PIAZZA_ENDPOINT', 'PIAZZA_KEY', 'PIAZZA_SECRET'], -1)


def view(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    lti_params = {
        "lti_message_type": "basic-lti-launch-request",
        "lti_version": "LTI-1p0",

        "resource_link_id": "120988f929-274612",
        "resource_link_title": "Weekly Blog",
        "resource_link_description": "A weekly blog.",
        "user_id": "8321264",
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
    }

    # settings for OAuth
    signatures = {
        "consumer_key": database_dot_py_config.PIAZZA_KEY, 
        "shared_secret": database_dot_py_config.PIAZZA_SECRET
    }
    
    oauthsimple = OAuthSimple()
    signed_request = oauthsimple.sign({
        'path': database_dot_py_config.PIAZZA_ENDPOINT,
        'action': "POST",
        'parameters': lti_params, 
        'signatures': signatures,
    })
    # tack the signature along with all the other things we're setting
    lti_params['oauth_signature'] = signed_request['signature']

    form = PiazzaAuthForm(initial=lti_params)

    return render_to_response('forums/piazza.html', 
                {'common_page_data': common_page_data, 
                'form': form, 
                'piazza_target_url': database_dot_py_config.PIAZZA_ENDPOINT},
            context_instance=RequestContext(request))

