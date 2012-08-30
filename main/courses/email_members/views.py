# Create your views here.
from courses.email_members.forms import EmailForm
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from courses.actions import auth_is_course_admin_view_wrapper
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from smtplib import SMTPDataError

@sensitive_post_parameters()
@csrf_protect
@auth_is_course_admin_view_wrapper
def email_members(request, course_prefix, course_suffix):
    """
    Displays the email form and handles email actions
    Right now this is blocking and does not do any batching.
    Will have to make it better
    """
    error_msg=""
    success_msg=""
    form = EmailForm()
    if request.method == "POST":
        form = EmailForm(data=request.POST)
        if form.is_valid():
            sender = request.common_page_data['course_prefix'] + "_no_reply@class.stanford.edu"
            sender = 'c2g-dev@cs.stanford.edu'
            message = render_to_string('email/email_autogen.txt', 
                                       {'course':request.common_page_data['course'],
                                        'url':request.build_absolute_uri(reverse('courses.views.main', args=[course_prefix, course_suffix])),
                                        'message':form.cleaned_data['message'],
                                        'common_page_data':request.common_page_data,
                                       },
                                       RequestContext(request))
            recipient_qset = User.objects.none() #get recipients in a QuerySet
            if form.cleaned_data['to'] == "all" :
                recipient_qset = request.common_page_data['course'].get_all_members()
            elif form.cleaned_data['to'] == "students" :
                recipient_qset = request.common_page_data['course'].get_all_students()
            elif form.cleaned_data['to'] == "staff" :
                recipient_qset = request.common_page_data['course'].get_all_course_admins()
            emails = map(lambda u: 
                             (form.cleaned_data['subject'], message, sender, [u.email]), 
                         list(recipient_qset))
            try:
                send_mass_mail(emails,fail_silently=False)
                success_msg="Your email was successfully sent"
                form = EmailForm()
            except SMTPDataError as sde:
                error_msg = "An error occurred when connecting with the mail server: " + sde.__str__()
        else:
            error_msg = "Please fix the errors below:"
    
    context = RequestContext(request)
    return render_to_response('email/email.html',
                              {'form': form,
                              'error_msg': error_msg,
                              'success_msg': success_msg,
                              'course': request.common_page_data['course'],
                              'common_page_data': request.common_page_data},
                              context_instance=context)
