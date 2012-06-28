from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^forums/list/(?P<course_id>\d+/', 'forums.views.list'),
	url(r'^forums/view/(?P<forum_id>\d+/', 'forums.views.view'),
)
