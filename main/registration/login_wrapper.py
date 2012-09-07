from django.contrib.auth import views as auth_views

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
import urlparse
import settings
from django.shortcuts import redirect
from c2g.util import redirects_use_http, upgrade_to_https_and_downgrade_upon_redirect


@sensitive_post_parameters()
@csrf_protect
@never_cache
@upgrade_to_https_and_downgrade_upon_redirect #here's the https wrapper
def ssl_wrapped_login(request, template_name='registration/login.html',
                   redirect_field_name=REDIRECT_FIELD_NAME,
                   authentication_form=AuthenticationForm,
                   current_app=None, extra_context=None):
    response=auth_views.login(request, template_name=template_name, redirect_field_name=redirect_field_name,  authentication_form=authentication_form, current_app=current_app, extra_context=extra_context)
    return response


