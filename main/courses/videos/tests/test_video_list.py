from test_harness.test_base import AuthenticatedTestBase

__all__ = ['VideoListStudentReadyModeTest']

class VideoListStudentReadyModeTest(AuthenticatedTestBase):
    """Simple existence checks for various features of video list page."""

    def __init__(self, *arrgs, **kwargs):
        config = { 'username' : 'student_0',
                   'password' : 'class2go',
                   'course_prefix' :'networking',
                   'course_suffix' :'Fall2012',
                   'mode' : 'ready' }
        if kwargs != None:
            kwargs.update(config)
        else:
            kwargs = config
        super(VideoListStudentReadyModeTest, self).__init__(*arrgs, **kwargs)

    def test_basic_page_access(self):
        """Tests that we can access the video list page

        url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/videos/?$', 'courses.videos.views.list'),
        """
        resp = self.client.get('/networking/Fall2012/videos' )
        self.assertEqual(resp.status_code, 200)

    def test_javascript_delivery(self):
        """Make sure video list js content is delivered exactly once"""
        resp = self.client.get('/networking/Fall2012/videos' )
        self.assertEqual(resp.content.count("function record_video_download("), 1)

