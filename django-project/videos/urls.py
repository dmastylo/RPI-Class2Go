from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^videos/list/(?P<course_id>\d+/', 'videos.views.list'),
	url(r'^videos/view/(?P<video_id>\d+/', 'videos.views.view'),
)
