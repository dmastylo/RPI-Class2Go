from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^all/', 'courses.views.all'),
	url(r'^current/', 'courses.views.current'),
	url(r'^edit/(?P<course_id>\d+)/', 'courses.views.edit'),
	url(r'^members/(?P<course_id>\d+)/', 'courses.views.members'),
	url(r'^mine/', 'courses.views.mine'),
	url(r'^new/', 'courses.views.new'),
	url(r'^(?P<course_id>\d+)/', 'courses.views.view'),
)
