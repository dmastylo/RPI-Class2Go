# Create your views here.
from courses.email_members.forms import EmailForm
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from courses.actions import auth_is_course_admin_view_wrapper
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from c2g.models import CourseEmail, EmailAddr
import courses.email_members.tasks
import pdb
import datetime
from hashlib import md5


def optout(request,code):
    """Opts mailing list members out of email we sent
    """
    email=""
    email_list=[]
    addr_qset=EmailAddr.objects.filter(optout_code=code)
    for addr in addr_qset.iterator():
        addr.optout=True
        addr.save()
        email_list.append(addr.addr)
    return render_to_response('email/optout.html',
                          {'email_list': email_list,},
                          context_instance=RequestContext(request))


    
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
    if request.session.get('email_subject') or request.session.get('email_message'):
        form = EmailForm({'subject': request.session['email_subject'], 'message': request.session['email_message']})
        del request.session['email_subject']
        del request.session['email_message']
    if request.method == "POST":
        form = EmailForm(data=request.POST)
        if form.is_valid():
            course = request.common_page_data['course']
            email = CourseEmail(course=request.common_page_data['course'],
                                sender=request.user,
                                to=form.cleaned_data['to'],
                                subject=form.cleaned_data['subject'],
                                html_message=form.cleaned_data['message'],
                                hash=md5((form.cleaned_data['message']+form.cleaned_data['subject']+datetime.datetime.isoformat(datetime.datetime.now())).encode('utf-8')).hexdigest())
            email.save()
            
            recipient_qset = User.objects.none() #get recipients in a QuerySet
            if form.cleaned_data['to'] == "all" :
                recipient_qset = request.common_page_data['course'].get_all_members()
            elif form.cleaned_data['to'] == "students" :
                recipient_qset = request.common_page_data['course'].get_all_students()
            elif form.cleaned_data['to'] == "staff" :
                recipient_qset = request.common_page_data['course'].get_all_course_admins()
            elif form.cleaned_data['to'] == "myself":
                recipient_qset = User.objects.filter(id=request.user.id)
            courses.email_members.tasks.delegate_emails.delay(email.hash,
                                                              recipient_qset.count(),
                                                              request.common_page_data['course'].title,
                                                              request.common_page_data['course'].handle,
                                                              request.build_absolute_uri(reverse('courses.views.main', args=[course_prefix, course_suffix])),
                                                              recipient_qset.query
                                                             )
            success_msg = "Your email was successfully queued for sending.  Please note that for large public classes (~10k), it may take 1-2 hours to send all emails."
            
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

@sensitive_post_parameters()
@csrf_protect
@auth_is_course_admin_view_wrapper
def email_members_old(request, course_prefix, course_suffix):
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
            sender = request.common_page_data['course'].title + ' Staff <class2go-noreply@cs.stanford.edu>'
            
            recipient_qset = User.objects.none() #get recipients in a QuerySet
            
            if form.cleaned_data['to'] == "all" :
                recipient_qset = request.common_page_data['course'].get_all_members()
            elif form.cleaned_data['to'] == "students" :
                recipient_qset = request.common_page_data['course'].get_all_students()
            elif form.cleaned_data['to'] == "staff" :
                recipient_qset = request.common_page_data['course'].get_all_course_admins()
            elif form.cleaned_data['to'] == "myself":
                recipient_qset = User.objects.filter(id=request.user.id)
            #pdb.set_trace()
            courses.email_members.tasks.email_with_celery.delay(
                                                                form.cleaned_data['subject'],
                                                                form.cleaned_data['message'],
                                                                sender,
                                                                recipient_qset.values_list('email',flat=True),
                                                                course_title=request.common_page_data['course'].title,
                                                                course_url=request.build_absolute_uri(reverse('courses.views.main', args=[course_prefix, course_suffix])))
            success_msg = "Your email was successfully queued for sending"
        #form = EmailForm()
        
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

