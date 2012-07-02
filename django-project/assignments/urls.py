from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^list/(?P<course_id>\d+)/', 'assignments.views.list'),
	url(r'^view/(?P<assignment_id>\d+)/', 'assignments.views.view'),
	url(r'^grade/(?P<assignment_id>\d+)/', 'assignments.views.grade'),
)
