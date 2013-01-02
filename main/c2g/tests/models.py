import os
import tempfile

#from django.contrib.auth.models import Group
from django.core.files import File as FieldFile
from test_harness.test_base import SimpleTestBase

from c2g.models import Course
from c2g.models import File as FileModel
#from c2g.models import Institution

class FileUnitTests(SimpleTestBase):
    """Idempotent unit tests of the File model methods: nothing gets saved"""

    def setUp(self):
        """Create a *very* fake models.File object"""
        # XXX: we should use a real mocking library probably
        self.myFile = FileModel()
        fh, fpath = tempfile.mkstemp(suffix='.jpeg')
        self.myFile.file = FieldFile(open(fpath, 'w'))
        self.myFile.file.write('\n')

    def tearDown(self):
        """Clean up cruft from the test object"""
        self.myFile.file.close()
        os.remove(self.myFile.file.name)

    def test_icon_methods(self):
        """Check methods related to file icon assignment"""
        self.assertEqual(self.myFile.get_ext(), 'jpeg')
        self.assertEqual(self.myFile.get_icon_type(), 'picture')


class C2GUnitTests(SimpleTestBase):
    
#    def test_multisave(self):
#        """
#        Tests saving a course more than once
#        """
#        numGroupsB4=len(Group.objects.all())
#        i=Institution(title='TestInstitute')
#        i.save()
#        course1=Course(institution=i,title='gack',handle='test--course')
#        course1.save()
#        course1.title='hack'
#        course1.save()
#        numGroupsAfter=len(Group.objects.all())
#        self.assertEqual(numGroupsB4+4, numGroupsAfter)

#    def test_course_create(self):
#        """
#        Tests that course creation creates groups
#        """
#        numGroupsB4=len(Group.objects.all())
#        i=Institution(title='TestInstitute')
#        i.save()
#        course1=Course(institution=i,title='gack',handle='test--course')
#        course1.save()
#        numGroupsAfter=len(Group.objects.all())
#        self.assertEqual(numGroupsB4+4, numGroupsAfter)

    def test_fixture_install(self):
        """
        Tests that fixtures were installed correctly
        """
        self.assertEqual(len(Course.objects.all()),4)
                         
        c = Course.objects.filter(handle='networking--Fall2012', mode = 'ready')
        for ci in c: 
            self.assertEqual(ci.title, u'Natural Language Processing')

        c = Course.objects.filter(handle='crypto--Fall2012', mode = 'ready')
        for ci in c:
            self.assertEqual(ci.title, u'Introductory Cryptography')
                               
    def test_index_page(self):
        """
        Tests that we can access the index page
        """
        resp=self.client.get('/')
        self.assertEqual(resp.status_code,200)
