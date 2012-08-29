from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url('^$',       'kelvinator.views.nobodyhome'),
    url('^_health', 'kelvinator.views.healthcheck'),
    url('^extract', 'kelvinator.views.extract'),
)
