# Create your views here.
#from django import form
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader, RequestContext
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render_to_response
from django.contrib.auth import logout

from c2g.models import Course
from accounts.forms import *

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")


def profile(request):
    course_list = Course.objects.all()
    groups = request.user.groups.all()
    courses = []
    for g in groups:
        for c in course_list:
            if g.id == c.student_group_id or g.id == c.instructor_group_id or g.id == c.tas_group_id or g.id == c.readonly_tas_group_id:
                courses.append(c)
                break

    return render_to_response('accounts/profile.html', {'request': request, 'courses': courses}, context_instance=RequestContext(request))

def edit(request):
    uform = EditUserForm(instance=request.user)
    pform = EditProfileForm(instance=request.user.get_profile())
    return render_to_response('accounts/edit.html', {'request':request, 'uform':uform, 'pform':pform}, context_instance=RequestContext(request))

def save_edits(request):
    uform = EditUserForm(request.POST, instance=request.user)
    pform = EditProfileForm(request.POST, instance=request.user.get_profile())
    if uform.is_valid() and pform.is_valid():
        uform.save()
        pform.save()
        return HttpResponseRedirect(reverse('accounts.views.profile'))
    
    return render_to_response('accounts/edit.html', {'request':request, 'uform':uform, 'pform':pform}, context_instance=RequestContext(request))

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

    
@never_cache
def shib_login(request):
    string = ""
    for k in request.META:
        string += k + " : " + str(request.META[k]) + "<br />"
    return HttpResponse(string)
