import json
import random
import string
import urlparse

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader, RequestContext
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render_to_response
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib.auth import get_backends, REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, authenticate as auth_authenticate
from django.contrib import messages
from django.contrib.auth.models import User, Group
from c2g.models import Course, Institution,Video, Instructor, CourseInstructor
from accounts.forms import *
from registration import signals
from registration.login_wrapper import login as auth_login_view
from registration.forms import RegistrationFormUniqueEmail
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from c2g.util import upgrade_to_https_and_downgrade_upon_redirect
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from pysimplesoap.client import SoapClient
from datetime import date

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")

def profile(request):
    
    user = request.user
    group_list = user.groups.all()
    courses = Course.objects.filter(Q(student_group_id__in=group_list, mode='ready') | Q(instructor_group_id__in=group_list, mode='ready') | Q(tas_group_id__in=group_list, mode='ready') | Q(readonly_tas_group_id__in=group_list, mode='ready'))
    
    user_profile = None
    is_student_list = []
    certs_list = {}
    longest_certlist = 0
    if user.is_authenticated():
        user_profile = user.get_profile()
        is_student_list = user_profile.is_student_list(group_list, courses)

        for cert in user_profile.certificates.all():
            certinfo = (cert.type, cert.dl_link(user))
            if certs_list.has_key(cert.course_id):
                certs_list[cert.course_id].append(certinfo)
                this_certlist = len(certs_list[cert.course_id])
                if longest_certlist < this_certlist:
                    longest_certlist = this_certlist
            else:
                certs_list[cert.course_id] = [certinfo]
                if longest_certlist == 0: longest_certlist = 1

    has_webauth = False
    if user.is_authenticated() and (user_profile.institutions.filter(title='Stanford').exists()):
        has_webauth = True

    return render_to_response('accounts/profile.html',
                              {
                                  'request': request,
                                  'courses': courses,
                                  'is_student_list': is_student_list,
                                  'has_webauth': has_webauth,
                                  'user_profile': user_profile,
                                  'certifications': certs_list,
                                  'longest_certs': range(longest_certlist),
                              },
                              context_instance=RequestContext(request))

def edit(request):
    uform = None
    pform = None
    if request.user.is_authenticated():
        uform = EditUserForm(instance=request.user)
        pform = EditProfileForm(instance=request.user.get_profile())
    
    has_webauth = False
    if request.user.is_authenticated() and (request.user.get_profile().institutions.filter(title='Stanford').exists()):
        has_webauth = True

    return render_to_response('accounts/edit.html', {'request':request, 'uform':uform, 'pform':pform, 'has_webauth': has_webauth,}, context_instance=RequestContext(request))

@csrf_protect
def save_edits(request):
    uform = EditUserForm(request.POST, instance=request.user)
    pform = EditProfileForm(request.POST, instance=request.user.get_profile())
    if uform.is_valid() and pform.is_valid():
        uform.save()
        pform.save()
        return HttpResponseRedirect(reverse('accounts.views.profile'))
    
    return render_to_response('accounts/edit.html', {'request':request, 'uform':uform, 'pform':pform}, context_instance=RequestContext(request))

@csrf_protect
@require_POST
def save_piazza_opts(request):
    email = request.POST.get('email')
    name = request.POST.get('name')
    str_id = request.POST.get('id')
    try:
        validate_email(email)
    except ValidationError:
        return HttpResponseBadRequest('You did not enter a valid email address.')
    try:
        nameValidator = RegexValidator(regex=r'^[\w -]+$')
        nameValidator(name.strip())
    except ValidationError:
        return HttpResponseBadRequest('Names on Piazza should only contain letters, numbers, underscores, hyphens, and spaces.')
    try:
        int_id = int(str_id)
    except ValueError:
        return HttpResponseBadRequest('Not a integer id')
    try:
        user = User.objects.get(id=str_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest('User not found')

    profile=user.get_profile()
    profile.piazza_name=name
    profile.piazza_email=email
    profile.save()
    return HttpResponse("Successfully Saved Piazza Options")


def logout(request):
    logout(request)
    return redirect('c2g.views.home')

@sensitive_post_parameters()
@csrf_protect
@never_cache
def register(request, template_name='accounts/register.html'):
    form=AuthenticationForm(request)
    t=loader.get_template(template_name)
    c=Context({
        'test': 'test',       
        'form': form,
    });
    return HttpResponse(t.render(c))

def impersonate(request,username):
    if not request.user.is_superuser:
        return HttpResponse('Permission denied')
    try:
        u1 = User.objects.get(username=username)
        u1.backend = 'django.contrib.auth.backends.ModelBackend'
    except User.DoesNotExist:
        return HttpResponse('User not found')
    auth_logout(request)
    auth_login(request,u1)
    return HttpResponse('You are now logged in as ' + username)

@never_cache
def default_preview_login(request, course_prefix, course_suffix):
    if settings.SITE_NAME_SHORT == "Stanford":
        return standard_preview_login(request, course_prefix, course_suffix)
    else:
        return ldap_preview_login(request, course_prefix, course_suffix)
    
@never_cache
def default_login(request):
 
    if request.method == 'GET':
        extra_context = {}
        context = RequestContext(request)
        for key, value in extra_context.items():
            context[key] = callable(value) and value() or value
        return render_to_response('registration/login.html',
                            {'form': AuthenticationForm, 'next': request.GET.get('next', '/')},
                            context_instance=context)
    else:
        if settings.SITE_NAME_SHORT == "Stanford":
            return auth_login_view(request)
        else:
            return ldap_login(request, '', '')


@never_cache
def shib_login(request):
    
    #check if there is valid remote user.
    #if one exists, try to match them
    #if one does not exist, create it and assign to proper institution
    #then redirect
    
    #setup the redirect first: code borrowed from django contrib library
    redir_to = request.GET.get('next', '/accounts/profile')
    netloc = urlparse.urlparse(redir_to)[1]
       
    # Heavier security check -- don't allow redirection to a different
    # host.
    if netloc and netloc != request.get_host():
        redir_to = '/accounts/profile'
                
    #Use EduPersonPrincipalName http://www.incommonfederation.org/attributesummary.html#eduPersonPrincipal
    #as username in our system.  We could support other persistent identifiers later, but it will take some
    #work
    if ('REMOTE_USER' in request.META) and ('eppn' in request.META) and (request.META['REMOTE_USER']==request.META['eppn']) and request.META['eppn']:
        
        #if we get here, the user has authenticated properly
        
        shib = {'givenName':'',
                'sn':'',
                'mail':'',
                'affiliation':'',
                'Shib-Identity-Provider':'',}
        
        shib.update(request.META)
        #Clean up first name, last name, and email address
        shib['sn'] = string.split(shib['sn'],";")[0]
        shib['givenName'] = string.split(shib['givenName'],";")[0]
        if not shib['mail']:
            shib['mail'] = shib['eppn']

        if not User.objects.filter(username=shib['REMOTE_USER']).exists():
            #here, we need to create the new user
            ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            rg = random.SystemRandom(random.randint(0,100000))
            password = (''.join(rg.choice(ALPHABET) for i in range(16))) + '1' #create a random password, which they will never use
            User.objects.create_user(shib['REMOTE_USER'], shib['mail'], password)
            # authenticate() always has to be called before login(), and
            # will return the user we just created.
            new_user = auth_authenticate(username=shib['REMOTE_USER'], password=password)

            new_user.first_name, new_user.last_name = shib['givenName'].capitalize(), shib['sn'].capitalize()
            new_user.save()
                
            profile = new_user.get_profile()
            profile.site_data = shib['affiliation']
            
            if 'stanford.edu' in shib['affiliation']:
                profile.institutions.add(Institution.objects.get(title='Stanford'))
                profile.save()
        
            auth_login(request, new_user)

            signals.user_registered.send(sender=__file__,
                             user=new_user,
                             request=request)

        else:
            #User already exists, so log him/her in
            user = User.objects.get(username=shib['REMOTE_USER'])
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            #determine whether to clear any "you must log in" messages
            clear_msgs = False
            storage = messages.get_messages(request)
            for message in storage:
                if "You must be logged-in" in message.message:
                    clear_msgs = True
            storage.used = clear_msgs

            messages.add_message(request,messages.SUCCESS, 'You have successfully logged in!')

    else:
        messages.add_message(request,messages.ERROR, 'WebAuth did not return your identity to us!  Please try logging in again.  If the problem continues please contact c2g-techsupport@class.stanford.edu')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    return HttpResponseRedirect(redir_to) 

# login for public courses
# @jbau here (1/25/2013).  I've removed the call to this since it was buggy.
# Now default_login just uses django.contrib.auth.views.login
def standard_login(request):
    
    #setup the redirect first: code borrowed from django contrib library
    redir_to = request.GET.get('next', '/')
    netloc = urlparse.urlparse(redir_to)[1]
       
    # Heavier security check -- don't allow redirection to a different
    # host.
    if netloc and netloc != request.get_host():
        redir_to = '/'
            
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        return HttpResponseRedirect(redir_to)

    else:                
        messages.add_message(request,messages.ERROR, 'WebAuth did not return your identity to us!  Please try logging in again.  If the problem continues please contact c2g-techsupport@class.stanford.edu')
        extra_context = {}
        context = RequestContext(request)
        for key, value in extra_context.items():
            context[key] = callable(value) and value() or value
        layout = {'m': 800}
        
        return render_to_response('registration/login.html',
                              {'form': form, 'layout': json.dumps(layout)},
                              context_instance=context)

@upgrade_to_https_and_downgrade_upon_redirect
def standard_preview_login(request, course_prefix, course_suffix):
    
    # check if username exists to find out what type of user 
    # this ensures that we don't unecessarily do the ldap auth
    
    login_form = AuthenticationForm(data=request.POST)
    if login_form.is_valid():
        auth_login(request, login_form.get_user())
            
        if not request.common_page_data['course'].preview_only_mode and \
            date.today() >= request.common_page_data['course'].calendar_start :
            redirect_to = 'courses.views.main'
        else:
            redirect_to = 'courses.preview.views.preview'
   
        return redirect(reverse(redirect_to, args=[course_prefix, course_suffix]))
       
    else:
        form_class = RegistrationFormUniqueEmail
        form = form_class(initial={'course_prefix':course_prefix,'course_suffix':course_suffix})
        context = RequestContext(request)                
       
        try:
            video = Video.objects.getByCourse(course=request.common_page_data['course']).get(slug='intro')
        except Video.DoesNotExist:
            video = None
   
        course_instructors = CourseInstructor.objects.getByCourse(course=request.common_page_data['course'])
        
        instructors = []
    
        for ci in course_instructors:
            instructors.append(ci.instructor)
  
        template_name='previews/default.html'

        return render_to_response(template_name,
                         {'form': form,
                          'login_form': login_form,
                          'video':video,
                          'instructors':instructors,
                          'common_page_data': request.common_page_data,
                          'course': request.common_page_data['course'],
                          'display_login': True},
                          context_instance=context)
       

    

@never_cache
def ldap_login(request, course_prefix, course_suffix):
    
    #check if there is valid remote user.
    #if one exists, try to match them
    #if one does not exist, create it and assign to proper institution
    #then redirect

    #setup the redirect first: code borrowed from django contrib library
    redir_to = request.GET.get('next', '/')
    netloc = urlparse.urlparse(redir_to)[1]
       
    # Heavier security check -- don't allow redirection to a different
    # host.
    if netloc and netloc != request.get_host():
        redir_to = '/'
        
    
    # check if username exists to find out what type of user 
    # this ensures that we don't unecessarily do the ldap auth
    
    is_institution_logon = False
    user_exists = False
    
    username = request.POST['username']
    password = request.POST['password'] 
    
    user_exists = User.objects.filter(username=username).exists()
    
    if user_exists:
        user = User.objects.get(username=username)
        is_institution_logon = user.get_profile().site_data == "UWA"

    result = 'error'
    
    if not user_exists or (user_exists and is_institution_logon):    
        client = SoapClient(wsdl="https://www.socrates.uwa.edu.au/tisi/commonws.asmx?wsdl", trace=True)
        response = client.UserAuth(userName=request.POST['username'],password=request.POST['password'])
        result = response['UserAuthResult']
    
    if 'error' in result:
        ''' Now try and do regular auth
        '''
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redir_to)

        else:                
            messages.add_message(request,messages.ERROR, 'WebAuth did not return your identity to us!  Please try logging in again.  If the problem continues please contact c2g-techsupport@class.stanford.edu')
            extra_context = {}
            context = RequestContext(request)
            for key, value in extra_context.items():
                context[key] = callable(value) and value() or value
            layout = {'m': 800}
        
            return render_to_response('registration/login.html',
                              {'form': form, 'layout': json.dumps(layout)},
                              context_instance=context)

    
    ldapUser = json.loads(result) 
 
    if not User.objects.filter(username=request.POST['username']).exists():
            #here, we need to create the new user
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        rg = random.SystemRandom(random.randint(0,100000))
        password = (''.join(rg.choice(ALPHABET) for i in range(16))) + '1' #create a random password, which they will never use
        
        User.objects.create_user(username, ldapUser[0]['mail'], password)
        User.objects.create_user    
        # authenticate() always has to be called before login(), and
        # will return the user we just created.
        new_user = auth_authenticate(username=username, password=password)

        new_user.first_name, new_user.last_name = ldapUser[0]['givenname'].capitalize(), ldapUser[0]['sn'].capitalize()
        new_user.save()
        
        print new_user         
        profile = new_user.get_profile()
        profile.site_data = 'UWA'
            
        profile.institutions.add(Institution.objects.get(title='UWA'))
        profile.save()
        
        auth_login(request, new_user)

        signals.user_registered.send(sender=__file__,
                             user=new_user,
                             request=request)

        return HttpResponseRedirect(request.GET.get('next', '/accounts/profile'))
    
    else:
            #User already exists, so log him/her in
        user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        messages.add_message(request,messages.SUCCESS, 'You have successfully logged in!')


    return HttpResponseRedirect(redir_to)


@never_cache
def ldap_preview_login(request, course_prefix, course_suffix):
    
    # check if username exists to find out what type of user 
    # this ensures that we don't unecessarily do the ldap auth
    
    is_institution_logon = False
    user_exists = False
    
    username = request.POST['username']
    password = request.POST['password'] 
    
    user_exists = User.objects.filter(username=username).exists()
    
    if user_exists:
        user = User.objects.get(username=username)
        is_institution_logon = user.get_profile().site_data == "UWA"

    result = 'error'
    
    if not user_exists or (user_exists and is_institution_logon):    
        client = SoapClient(wsdl="https://www.socrates.uwa.edu.au/tisi/commonws.asmx?wsdl", trace=True)
        response = client.UserAuth(userName=request.POST['username'],password=request.POST['password'])
        result = response['UserAuthResult']
    
    if 'error' in result:
        ''' Now try and do regular auth
        '''
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            auth_login(request, login_form.get_user())
            
            if not request.common_page_data['course'].preview_only_mode and \
                date.today() >= request.common_page_data['course'].calendar_start :
                redirect_to = 'courses.views.main'
            else:
                redirect_to = 'courses.preview.views.preview'
        
            return redirect(reverse(redirect_to, args=[course_prefix, course_suffix]))
            
        else:
            form_class = RegistrationFormUniqueEmail
            form = form_class(initial={'course_prefix':course_prefix,'course_suffix':course_suffix})
            context = RequestContext(request)                
            
            try:
                video = Video.objects.getByCourse(course=request.common_page_data['course']).get(slug='intro')
            except Video.DoesNotExist:
                video = None
        
            course_instructors = CourseInstructor.objects.getByCourse(course=request.common_page_data['course'])
            instructors = []
    
            for ci in course_instructors:
                instructors.append(ci.instructor)
            
            template_name='previews/default.html'

            return render_to_response(template_name,
                              {'form': form,
                               'login_form': login_form,
                               'video':video,
                               'instructors':instructors,
                               'common_page_data': request.common_page_data,
                               'course': request.common_page_data['course'],
                               'display_login': True},
                               context_instance=context)
            
 
    
    ldapUser = json.loads(result)
 
    if not User.objects.filter(username=request.POST['username']).exists():
            #here, we need to create the new user
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        rg = random.SystemRandom(random.randint(0,100000))
        password = (''.join(rg.choice(ALPHABET) for i in range(16))) + '1' #create a random password, which they will never use
        
        User.objects.create_user(username, ldapUser[0]['mail'], password)
        User.objects.create_user    
        # authenticate() always has to be called before login(), and
        # will return the user we just created.
        new_user = auth_authenticate(username=username, password=password)

        new_user.first_name, new_user.last_name = ldapUser[0]['givenname'].capitalize(), ldapUser[0]['sn'].capitalize()
        new_user.save()
        
        print new_user         
        profile = new_user.get_profile()
        profile.site_data = 'UWA'
            
        profile.institutions.add(Institution.objects.get(title='UWA'))
        profile.save()
        
        auth_login(request, new_user)

        signals.user_registered.send(sender=__file__,
                             user=new_user,
                             request=request)

#        return HttpResponseRedirect(request.GET.get('next', '/accounts/profile'))
    
    else:
            #User already exists, so log him/her in
        user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
#        messages.add_message(request,messages.SUCCESS, 'You have successfully logged in!')


    if not request.common_page_data['course'].preview_only_mode and \
                date.today() >= request.common_page_data['course'].calendar_start :
        redirect_to = 'courses.views.main'
    else:
        redirect_to = 'courses.preview.views.preview'
        
    return redirect(reverse(redirect_to, args=[course_prefix, course_suffix]))

