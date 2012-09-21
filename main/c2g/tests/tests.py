from django.test import TestCase
from c2g.models import Institution, Course
from django.contrib.auth.models import Group 
from db_test_data.management.commands.db_populate import Command 

class C2GUnitTests(TestCase):
    
    pop_command = Command()
    #fixtures=['db_snapshot.json']
    
    def setUp(self):
        self.pop_command.handle()

    
    def tearDown(self):
        pass
    
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
