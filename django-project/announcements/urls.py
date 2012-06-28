from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^announcements/list/(?P<course_id>\d+/', 'announcements.views.list'),
)
