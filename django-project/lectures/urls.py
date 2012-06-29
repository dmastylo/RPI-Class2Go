from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^lectures/list/(?P<course_id>\d+/', 'lectures.views.list'),
	url(r'^lectures/view/(?P<lecture_id>\d+/', 'lectures.views.view'),
)
