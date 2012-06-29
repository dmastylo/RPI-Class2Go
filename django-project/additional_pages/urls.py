from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('additional_pages.views',
    url(r'^list/(?P<course_id>)\d+/', 'list'),
    url(r'^show/(?P<additional_page_id>)\d+/', 'show'),
)
