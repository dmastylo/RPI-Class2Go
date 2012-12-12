import os
import tempfile

from django.core.files import File as FieldFile

from c2g.models import File as FileModel
#from c2g.models import ContentGroup as ContentGroupModel
from c2g.models import ContentSection as ContentSectionModel
from test_harness.test_base import SimpleTestBase


class ContentGroupUnitTests(SimpleTestBase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


class ContentSectionUnitTests(SimpleTestBase):

    def setUp(self):
        super(ContentSectionUnitTests, self).setUp()
        self.course_id = 2   # first ready mode course
        self.section_id = 3  # selected because it's got few children
        self.fixture_data = [('video', 7L), ('video', 9L), ('video', 11L), ('problemSet', 3L)]
        self.contentsection = ContentSectionModel.objects.get(id=self.section_id)
        self.files = []

    def tearDown(self):
        for f in self.files:
            FileModel.objects.filter(title=f.title).delete()
        super(ContentSectionUnitTests, self).tearDown()

    def __manufacture_file(self, title='(unset title)'):
        fh, fpath = tempfile.mkstemp(suffix='.jpeg')
        course_handle = self.contentsection.course.handle
        new_f = FileModel(section=self.contentsection, title=title, file = FieldFile(open(fpath, 'w')), handle=course_handle)
        new_f.file.write('\n')
        new_f.save()
        new_f.image = new_f.create_ready_instance()
        new_f.image.save()
        self.files.append(new_f)
        return new_f

    def test_getChildren(self):
        """Test that ContentSection.getChildren behaves w/ various parameters"""
        untagged_sorted_children = self.contentsection.getChildren()
        tagged_sorted_children   = self.contentsection.getChildren(gettagged=True)
        tagged_unsorted_children = self.contentsection.getChildren(gettagged=True, getsorted=False)
        self.assertEqual(len(untagged_sorted_children), len(tagged_sorted_children))
        self.assertEqual(len(tagged_sorted_children), len(tagged_unsorted_children))
        self.assertEqual([item.id for item in untagged_sorted_children], [x[1] for x in self.fixture_data])
        self.assertEqual([(item['type'], item['item'].id) for item in tagged_sorted_children], self.fixture_data)

    def test_countChildren(self):
        """Test counting children of ContentSections using fixtures"""
        self.assertEqual(self.contentsection.countChildren(), len(self.fixture_data))


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

