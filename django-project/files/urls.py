from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^files/list/(?P<course_id>\d+/', 'files.views.list'),
)
