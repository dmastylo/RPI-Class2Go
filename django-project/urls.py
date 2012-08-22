from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Home page redirects to our one course page for now.  We will want to remove
    # this before we go to production of course.
    url(r'^$', redirect_to, {'url': '/nlp/Fall2012/'}),
    url(r'^nlp$', redirect_to, {'url': '/nlp/Fall2012/'}),

    # Health check endpoint.  Used by AWS load balancer.  Want something stable that
    # won't be redirected or change
    url(r'_health$', 'c2g.views.healthcheck'),

    # Examples:
    url(r'^courses/?$', 'c2g.views.home', name='c2g_home'),
    url(r'^courses/signup/?$', 'courses.actions.signup'),
    # url(r'^class2go/', include('class2go.foo.urls')),

     #for data collection
     url(r'^videos/save/', 'courses.videos.actions.save_video_progress'),
     url(r'^problemsets/attempt/(?P<problemId>\d+)/?$', 'problemsets.views.attempt'),

    # accounts app for user management
    url(r'^accounts/profile/?$', 'accounts.views.profile', name='accounts_profile'),
    url(r'^accounts/profile/edit/?', 'accounts.views.edit'),
    url(r'^accounts/profile/save_edits/?', 'accounts.views.save_edits'),

    url(r'^accounts/', include('registration.backends.simple.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    # The following line is temprarily commented out until we figure out how django cascades its URL matching operations.
    # After this is figured out, the rest of the matches below shall be moved to courses.url.
    #url(r'.*', include('courses.urls')),

    url(r'^courses/new/?', 'courses.admin_views.new'),

    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/?$', 'courses.views.main'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/materials/?$', 'courses.views.course_materials'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/admin/?', 'courses.admin_views.admin'),

    url(r'^switch_mode', 'courses.actions.switch_mode'),
    url(r'^add_section', 'courses.actions.add_section'),

    url(r'^commit/?', 'courses.actions.commit'),
    url(r'^revert/?$', 'courses.actions.revert'),
    url(r'^change_live_datetime/?', 'courses.actions.change_live_datetime'),

    # Additional Pages
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/pages/(?P<slug>[a-zA-Z0-9_-]+)/?$', 'courses.additional_pages.views.main'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/manage_nav_menu/?$', 'courses.additional_pages.views.manage_nav_menu'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/add_section_page/?$', 'courses.additional_pages.views.add_section_page'),
    url(r'^delete_page', 'courses.additional_pages.actions.delete'),
    url(r'^save_page', 'courses.additional_pages.actions.save'),
    url(r'^save_order', 'courses.additional_pages.actions.save_order'),
    url(r'^add_page', 'courses.additional_pages.actions.add'),

    # Announcements
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/announcements/?$', 'courses.announcements.views.list'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/announcements/admin/?$', 'courses.announcements.views.admin'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/announcements/(?P<announcement_id>[0-9]+)/edit/?$', 'courses.announcements.views.edit'),
    url(r'^save_announcement_order$', 'courses.announcements.actions.save_announcement_order'),
    url(r'^save_announcement$', 'courses.announcements.actions.save_announcement'),
    url(r'^add_announcement$', 'courses.announcements.actions.add_announcement'),
    url(r'^delete_announcement$', 'courses.announcements.actions.delete_announcement'),
    url(r'^email_announcement$', 'courses.announcements.actions.email_announcement'),


    # Forums
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/forums/?$', 'courses.forums.views.view'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/forums/admin/?', 'courses.forums.views.admin'),

    # Sections
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/sections/reorder/?$', 'courses.content_sections.views.reorder'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/sections/rename/(?P<section_id>[0-9]+)/?$', 'courses.content_sections.views.rename'),
    url(r'^rename$', 'courses.content_sections.actions.rename'),
    url(r'^save_content_section_order$', 'courses.content_sections.actions.save_order'),
    url(r'^delete_content_section$', 'courses.content_sections.actions.delete_content_section'),
    url(r'^save_content_section_content_order$', 'courses.content_sections.actions.save_content_order'),

    # Videos
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/videos/?$', 'courses.videos.views.list'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/videos/upload$', 'courses.videos.views.upload'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/videos/(?P<slug>[a-zA-Z0-9_-]+)/?$', 'courses.videos.views.view'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/videos/(?P<slug>[a-zA-Z0-9_-]+)/edit/?', 'courses.videos.views.edit'),
    url(r'^add_video/?$', 'courses.videos.actions.add_video'),
    url(r'^edit_video/?$', 'courses.videos.actions.edit_video'),
    url(r'^delete_video/?', 'courses.videos.actions.delete_video'),
    url(r'^upload_video/?', 'courses.videos.actions.upload'), ####ADDED BY KEVIN
    url(r'^oauth2callback/?', 'courses.videos.actions.oauth'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/videos/(?P<video_id>[a-zA-Z0-9_-]+)/load_video_problem_set?$', 'courses.videos.views.load_video_problem_set'),


    # Video Exercises
    url(r'^(?P<course_prefix>[a-zA-Z0-9_]+)/(?P<course_suffix>[a-zA-Z0-9_]+)/video_exercises/(?P<video_id>[a-zA-Z0-9_-]+)/?$', 'courses.video_exercises.views.view'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_]+)/(?P<course_suffix>[a-zA-Z0-9_]+)/videos/(?P<video_slug>[a-zA-Z0-9_-]+)/manage_exercises?$', 'courses.videos.views.manage_exercises'),
    url(r'^add_video_exercise/?$', 'courses.videos.views.add_exercise'),
    url(r'^add_existing_video_exercises/?$', 'courses.videos.views.add_existing_exercises'),
    url(r'^save_video_exercises/?', 'courses.videos.views.save_exercises'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_]+)/(?P<course_suffix>[a-zA-Z0-9_]+)/videos/?$', 'courses.videos.views.list'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/video_exercises/(?P<video_id>[a-zA-Z0-9_-]+)/?$', 'courses.video_exercises.views.view'),
    url(r'^get_video_exercises/?$', 'courses.videos.views.get_video_exercises'),


    #Problem Sets
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/problemsets/?$', 'problemsets.views.list'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)?$', 'problemsets.views.show'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/createproblemset/?$', 'problemsets.views.create_form'),
    url(r'^createproblemsetaction/?', 'problemsets.views.create_action'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)/edit?$', 'problemsets.views.edit_form'),
    url(r'^editproblemsetaction/?', 'problemsets.views.edit_action'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)/manage_exercises?$', 'problemsets.views.manage_exercises'),
    url(r'^add_existing_problemset_exercises/?$', 'problemsets.views.add_existing_exercises'),
    url(r'^save_problemset_exercises/?', 'problemsets.views.save_exercises'),
    url(r'^delete_exercise/?', 'problemsets.views.delete_exercise'),
    url(r'^delete_problemset/?', 'problemsets.actions.delete_problemset'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/exercises/(?P<exercise_name>.+)$', 'problemsets.views.read_exercise'),
    url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)/load_problem_set?$', 'problemsets.views.load_problem_set'),
)
