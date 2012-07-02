from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^list/(?P<course_id>\d+)/', 'videos.views.list'),
	url(r'^view/(?P<video_id>\d+)/', 'videos.views.view'),
)
