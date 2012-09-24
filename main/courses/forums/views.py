from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from courses.actions import auth_view_wrapper
from courses.forums.forms import PiazzaAuthForm
from database import PIAZZA_ENDPOINT, PIAZZA_KEY, PIAZZA_SECRET
from OAuthSimple import OAuthSimple

@auth_view_wrapper
def view(request, course_prefix, course_suffix):
    # Only use the ready course (for the piazza_id) since Piazza has no notion
    # of draft/live.
    course = request.common_page_data['ready_course']

    lti_params = {
        "lti_message_type": "basic-lti-launch-request",
        "lti_version": "LTI-1p0",
        "resource_link_id": "class2go-forum",
    }
    lti_params['user_id'] = request.user.id

    # TODO: once we get course policies in place, provide an override to enable using real
    # names (see #578)
    # 
    # lti_params['lis_person_name_family'] = request.user.last_name
    # lti_params['lis_person_name_given'] = request.user.first_name
    # lti_params['lis_person_name_full'] = request.user.first_name + " " + request.user.last_name

    lti_params['lis_person_name_full'] = request.user.username
    lti_params['lis_person_contact_email_primary'] = request.user.email

    # Piazza only supports two roles, instructor and strudent; TA's (readonly too) are instructors. 
    if request.common_page_data['is_course_admin']:
        lti_params['roles'] = "Instructor"
    else:
        lti_params['roles'] = "Student"

    lti_params['context_id'] = course.piazza_id
    lti_params['context_label'] = request.common_page_data['course_prefix']
    lti_params['context_title'] = course.title

    # Use OAuthSimple to sign the request. 
    signatures = {
        'consumer_key': PIAZZA_KEY,
        'shared_secret': PIAZZA_SECRET,
    }
    oauthsimple = OAuthSimple()
    signed_request = oauthsimple.sign({
        'path': PIAZZA_ENDPOINT,
        'action': "POST",
        'parameters': lti_params, 
        'signatures': signatures,
    })

    form = PiazzaAuthForm(initial=signed_request['parameters'])

    # Set common_page_data['can_switch_mode'] to false to hide mode switcher on this page.
    common_page_data['can_switch_mode'] = False
    
    return render_to_response('forums/piazza.html', {
            'common_page_data': request.common_page_data, 
            'form': form, 
            'piazza_target_url': PIAZZA_ENDPOINT,
        }, context_instance=RequestContext(request))

