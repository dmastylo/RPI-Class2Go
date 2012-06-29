from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'c2g.views.home'),
    # url(r'^class2go/', include('class2go.foo.urls')),

    # accounts app for user management
	url(r'^accounts/profile/', 'accounts.views.profile'),
	url(r'^accounts/', include('registration.backends.simple.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	
	url(r'^additional_pages/', include('additional_pages.urls')),
	url(r'^announcements/', include('announcements.urls')),
	url(r'^assignments/', include('assignments.urls')),
	url(r'^courses/', include('courses.urls')),
	url(r'^files/', include('files.urls')),
	url(r'^forums/', include('forums.urls')),
	url(r'^lectures/', include('lectures.urls')),
	url(r'^officehours/', include('officehours.urls')),
	url(r'^sections/', include('sections.urls')),
	url(r'^videos/', include('videos.urls')),
)
