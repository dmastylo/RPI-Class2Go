from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^additional_pages/list/(?P<course_id>\d+/', 'additional_pages.views.list'),
	url(r'^additional_pages/view/(?P<additional_page_id>\d+/', 'additional_pages.views.view'),
)
