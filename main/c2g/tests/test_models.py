import os
import tempfile

from django.core.files import File as FieldFile

from c2g.models import File as FileModel
#from c2g.models import ContentGroup as ContentGroupModel
#from c2g.models import ContentSection as ContentSectionModel
from test_harness.test_base import SimpleTestBase


class ContentGroupUnitTests(SimpleTestBase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


#class ContentSectionUnitTests(SimpleTestBase):
#
#    def setUp(self):
#        self.course_id = 2   # first ready mode course
#        self.section_id = 4  # selected because it's got few children
#        self.fixture_data = [('video', 8L),
#                             ('video', 10L),
#                             ('video', 12L),
#                             ('additional_page', 72L),
#                             ('file', 164L),
#                             ('file', 166L)]
#        self.contentsection = ContentSectionModel.objects.get(id=self.section_id)
#
#    def tearDown(self):
#        pass
#
##    def test_getChildren(self):
#        """Test that ContentSection.getChildren behaves w/ various parameters"""
#        untagged_sorted_children = self.contentsection.getChildren()
#        tagged_sorted_children   = self.contentsection.getChildren(gettagged=True)
#        tagged_unsorted_children = self.contentsection.getChildren(gettagged=True, getsorted=False)
#        self.assertEqual(len(untagged_sorted_children), len(tagged_sorted_children))
#        self.assertEqual(len(tagged_sorted_children), len(tagged_unsorted_children))
#        self.assertEqual([item.id for item in untagged_sorted_children], [x[1] for x in self.fixture_data])
#        self.assertEqual([(item['type'], item['item'].id) for item in tagged_sorted_children], self.fixture_data)
#        self.assertNotEqual([(item['type'], item['item'].id) for item in tagged_sorted_children],
#                            [(item['type'], item['item'].id) for item in tagged_unsorted_children])
#        self.assertItemsEqual([(item['type'], item['item'].id) for item in tagged_sorted_children],
#                              [(item['type'], item['item'].id) for item in tagged_unsorted_children])
#
#    def test_countChildren(self):
#        """Test counting children of ContentSections using fixtures"""
#        self.assertEqual(self.contentsection.countChildren(), 6)
#
#    def test_getNextIndex(self):
#        """Test next index generation of ContentSections using fixtures"""
#        def manufacture_file(title='(unset title)'):
#            fh, fpath = tempfile.mkstemp(suffix='.jpeg')
#            new_f = FileModel(section=self.contentsection, title=title, file = FieldFile(open(fpath, 'w')))
#            self.myFile.file.write('\n')
#            new_f.save()
#            new_f.image = new_f.create_read_instance()
#            new_f.image.save()
#            return new_f
#        next_index_shouldbe = 7
#        self.assertEqual(self.contentsection.getNextIndex(), next_index_shouldbe)
#        new_f_a = manufacture_file('(should be index 7)')
#        self.assertEqual(new_f_a.id, self.contentsection.getChildren()[next_index_shouldbe].id)
#        new_f_b = manufacture_file('(should be index 8)')
#        self.assertEqual(new_f_b.id, self.contentsection.getChildren()[next_index_shouldbe+1].id)
#        new_f_a.delete()
#        self.assertEqual(self.contentsection.getNextIndex(), next_index_shouldbe+2)
#        self.assertNotEqual(self.contentsection.getNextIndex(), self.contentSection.countChildren()+1)

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

