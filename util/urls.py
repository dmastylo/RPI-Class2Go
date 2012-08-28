from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url('^_health', 'kelvinator.views.healthcheck'),
    url('^extract', 'kelvinator.views.extract'),
)
