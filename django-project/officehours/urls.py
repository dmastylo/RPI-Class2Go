from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^officehours/list/(?P<course_id>\d+/', 'officehours.views.list'),
)
