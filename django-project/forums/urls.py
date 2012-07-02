from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^list/(?P<course_id>\d+)/', 'forums.views.list'),
	url(r'^view/(?P<forum_id>\d+)/', 'forums.views.view'),
)
