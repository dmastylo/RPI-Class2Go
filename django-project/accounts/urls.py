from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *

#import django.contrib.auth.views

urlpatterns = patterns('',
    url(r'^$', 'accounts.views.index'),
    url(r'^register/$','accounts.views.register'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'accounts/login.html'}, name="login-form"),
	url(r'^profile/$', 'accounts.views.profile'),
)
