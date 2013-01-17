# Create your views here.
#from django import form

import urlparse
import settings

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
from c2g.models import Course, Institution
from accounts.forms import *
from registration import signals
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
import random
import os
import string
import base64

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")


def profile(request):
    
    group_list = request.user.groups.all()
    courses = Course.objects.filter(Q(student_group_id__in=group_list, mode='ready') | Q(instructor_group_id__in=group_list, mode='ready') | Q(tas_group_id__in=group_list, mode='ready') | Q(readonly_tas_group_id__in=group_list, mode='ready'))
    
    if request.user.is_authenticated():
        user_profile = request.user.get_profile()
        is_student_list = user_profile.is_student_list(group_list, courses)
    else:
        user_profile = None
        is_student_list = []

    has_webauth = False
    if request.user.is_authenticated() and (request.user.get_profile().institutions.filter(title='Stanford').exists()):
        has_webauth = True

    return render_to_response('accounts/profile.html',
                              {'request': request,
                              'courses': courses,
                              'is_student_list': is_student_list,
                              'has_webauth': has_webauth,},
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
            messages.add_message(request,messages.SUCCESS, 'You have successfully logged in!')

    else:
        messages.add_message(request,messages.ERROR, 'WebAuth did not return your identity to us!  Please try logging in again.  If the problem continues please contact c2g-techsupport@class.stanford.edu')

    return HttpResponseRedirect(redir_to)
