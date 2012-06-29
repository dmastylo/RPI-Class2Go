from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^assignments/list/(?P<course_id>\d+/', 'assignments.views.list'),
	url(r'^assignments/view/(?P<asssignment_id>\d+/', 'assignments.views.view'),
	url(r'^assignments/grade/(?P<asssignment_id>\d+/', 'assignments.views.grade'),
)
