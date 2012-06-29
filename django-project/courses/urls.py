from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^courses/all/', 'courses.views.all'),
	url(r'^courses/current/', 'courses.views.current'),
	url(r'^courses/edit/(?P<course_id>\d+/', 'courses.views.edit'),
	url(r'^courses/members/(?P<course_id>\d+/', 'courses.views.members'),
	url(r'^courses/mine/', 'courses.views.mine'),
	url(r'^courses/new/', 'courses.views.new'),
	url(r'^courses/(?P<course_id>\d+/', 'courses.views.view'),
)
