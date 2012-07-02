from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^courses/all/', 'courses.views.all'),
	url(r'^courses/current/', 'courses.views.current'),
	url(r'^courses/mine/', 'courses.views.mine'),
	url(r'^(?P<course_id>\d+)/?$', 'courses.views.view'),
	
	url(r'^courses/new/', 'courses.admin_views.new'),
	url(r'^(?P<course_id>\d+)/admin', 'courses.admin_views.main'),
	url(r'^(?P<course_id>\d+)/edit', 'courses.admin_views.edit'),
	url(r'^(?P<course_id>\d+)/members', 'courses.admin_views.members'),
	
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/?$', 'courses.branches.views.view'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/admin', 'courses.branches.views.admin'),
	
	# Additional Pages
	url(r'^(?P<course_id>[a-z0-9_]+)/(?P<branch_id>[a-z0-9_]+)/additional_pages/?$', 'courses.additional_pages.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/additional_pages/admin', 'courses.additional_pages.views.admin'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/additional_pages/(?P<additional_page_id>\d+)', 'courses.additional_pages.views.view'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/additional_pages/(?P<additional_page_id>\d+)/edit', 'courses.additional_pages.views.edit'),

	# Announcements
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/announcements', 'courses.announcements.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/announcements/admin', 'courses.announcements.views.admin'),
	
	# Assignments
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/assignments', 'courses.assignments.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/assignments/admin', 'courses.assignments.views.admin'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/assignments/(?P<assignment_id>\d+)', 'courses.assignments.views.view'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/assignments/(?P<assignment_id>\d+)/edit', 'courses.assignments.views.edit'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/assignments/(?P<assignment_id>\d+)/grade', 'courses.assignments.views.grade'),
	
	# Files
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/files', 'courses.files.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/files/admin', 'courses.files.views.admin'),
	
	# Forums
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/forums', 'courses.forums.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/forums/admin', 'courses.forums.views.admin'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/forums/(?P<forum_id>\d+)', 'courses.forums.views.view'),
	
	# Lectures
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/lectures', 'courses.lectures.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/lectures/admin', 'courses.lectures.views.admin'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/lectures/(?P<lecture_id>\d+)', 'courses.lectures.views.view'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/lectures/(?P<lecture_id>\d+)/edit', 'courses.lectures.views.edit'),
	
	# Office Hours
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/officehours', 'courses.officehours.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/officehours/admin', 'courses.officehours.views.admin'),
	
	# Sections
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/sections', 'courses.sections.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/sections/admin', 'courses.sections.views.admin'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/sections/(?P<section_id>\d+)', 'courses.sections.views.view'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/sections/(?P<section_id>\d+)/edit', 'courses.sections.views.edit'),
	
	# Videos
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/videos', 'courses.videos.views.list'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/videos/admin', 'courses.videos.views.admin'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/videos/(?P<video_id>\d+)', 'courses.videos.views.view'),
	url(r'^(?P<course_id>\d+)/(?P<branch_id>\d+)/videos/(?P<video_id>\d+)/edit', 'courses.videos.views.edit'),
)
