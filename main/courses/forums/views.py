from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from courses.actions import auth_view_wrapper
from courses.forums.forms import PiazzaAuthForm
from c2g.models import PageVisitLog
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
        "lis_person_sourcedid": "class2go:user",
        "resource_link_id": "class2go-forum",
        "resource_link_title": "Class2Go",
        "resource_link_description": "Class2Go Forum",
        "tool_consumer_instance_guid": "class2go guid",
        "tool_consumer_instance_description": "Class2Go",
        "oauth_callback": "about:blank",
        "ext_submit": "Press To Launch"
    }
    lti_params['user_id'] = request.user.id

    # TODO: once we get course policies in place, provide an override to enable using real
    # names (see #578)
    # 
    # lti_params['lis_person_name_family'] = request.user.last_name
    # lti_params['lis_person_name_given'] = request.user.first_name
    # lti_params['lis_person_name_full'] = request.user.first_name + " " + request.user.last_name
            
    profile = request.user.get_profile()
    show_confirmation = False
    if (not profile.piazza_name):
        show_confirmation = True
        fullname = request.user.first_name + " " + request.user.last_name
        lti_params['lis_person_name_full'] = fullname.encode("utf-8")
    else:
        lti_params['lis_person_name_full'] = profile.piazza_name.encode("utf-8")
        
    if (not profile.piazza_email):
        show_confirmation = True
        lti_params['lis_person_contact_email_primary'] = request.user.email
    else:
        lti_params['lis_person_contact_email_primary'] = profile.piazza_email
            

    # Piazza only supports two roles, instructor and strudent; TA's (readonly too) are instructors. 
    if request.common_page_data['is_course_admin']:
        lti_params['roles'] = "Instructor"
    else:
        lti_params['roles'] = "Student"
        visit_log = PageVisitLog(
            course = course,
            user = request.user,
            page_type= 'forum',
        )
        visit_log.save()

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

    querystring = request.META['QUERY_STRING']

    # Set common_page_data['can_switch_mode'] to false to hide mode switcher on this page.
    request.common_page_data['can_switch_mode'] = False
    
    return render_to_response('forums/piazza.html', {
            'common_page_data': request.common_page_data,
            'show_confirmation': show_confirmation,
            'form': form,
            'piazza_target_url': PIAZZA_ENDPOINT,
            'querystring': querystring,
        }, context_instance=RequestContext(request))

