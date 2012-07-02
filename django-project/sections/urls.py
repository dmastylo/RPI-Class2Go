from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^list/(?P<course_id>\d+)/', 'sections.views.list'),
	url(r'^view/(?P<section_id>\d+)/', 'sections.views.view'),
)
