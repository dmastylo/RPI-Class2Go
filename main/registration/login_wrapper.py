from django.contrib.auth import views as auth_views

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from c2g.util import upgrade_to_https_and_downgrade_upon_redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required


@sensitive_post_parameters()
@csrf_protect
@never_cache
@upgrade_to_https_and_downgrade_upon_redirect #here's the https wrapper
def login(request, template_name='registration/login.html',
                   redirect_field_name=REDIRECT_FIELD_NAME,
                   authentication_form=AuthenticationForm,
                   current_app=None, extra_context=None):
    return auth_views.login(request, template_name=template_name, redirect_field_name=redirect_field_name,  authentication_form=authentication_form, current_app=current_app, extra_context=extra_context)
    


@sensitive_post_parameters()
@csrf_protect
@login_required
@upgrade_to_https_and_downgrade_upon_redirect #here's the https wrapper
def password_change(request,
                   template_name='registration/password_change_form.html',
                   post_change_redirect=None,
                   password_change_form=PasswordChangeForm,
                   current_app=None, extra_context=None):
    return auth_views.password_change(request, template_name=template_name, post_change_redirect=post_change_redirect,
                                     password_change_form=password_change_form,current_app=current_app,
                                     extra_context=extra_context)


@sensitive_post_parameters()
@never_cache
@upgrade_to_https_and_downgrade_upon_redirect #here's the https wrapper
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    return auth_views.password_reset_confirm(request, uidb36=uidb36, token=token, template_name=template_name,
                                             token_generator=token_generator, set_password_form=set_password_form,
                                             post_reset_redirect=post_reset_redirect, current_app=current_app,
                                             extra_context=extra_context)
