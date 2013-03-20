import os
import tempfile
import random
import re

#from django.contrib.auth.models import Group
from django.core.files import File as FieldFile
from test_harness.test_base import SimpleTestBase

from c2g.models import Course, Exam
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

    def test_num_questions(self):
        """
        Tests the num_questions function in the Exam() class.
        """
        badxml1="<"
        badxml2="<abc>"
        badxml3="<def />"
        badxml4="""<exam_metadata choosenquestions="" />"""
        badxml5="""<exam_metadata choosenquestions="baby" />"""
        xml1="<exam_metadata />"
        xml2="""<exam_metadata choosenquestions="3" />"""
        xml3="""<exam_metadata choosenquestions="542" />"""

        exam = Exam()
        exam.xml_metadata=badxml1
        self.assertEqual(exam.num_random_questions(),0)
        exam.xml_metadata=badxml2
        self.assertEqual(exam.num_random_questions(),0)
        exam.xml_metadata=badxml3
        self.assertEqual(exam.num_random_questions(),0)
        exam.xml_metadata=badxml4
        self.assertEqual(exam.num_random_questions(),0)
        exam.xml_metadata=badxml5
        self.assertEqual(exam.num_random_questions(),0)
        exam.xml_metadata=xml1
        self.assertEqual(exam.num_random_questions(),0)
        exam.xml_metadata=xml2
        self.assertEqual(exam.num_random_questions(),3)
        exam.xml_metadata=xml3
        self.assertEqual(exam.num_random_questions(),542)

    def test_get_html_basic(self):
        """
        Some basic unit tests of randomizing question divs.
        """
        preamble = "<p>This is a <b>preamble</b></p>"
        question_template = \
"""
<div class="question" id="problem_%d">
    <p>Q1</p>
</div>
"""
        badxml1="<abc>"
        xml_none = "<exam_metadata />"
        xml_template = '<exam_metadata choosenquestions="%d" />'
        exam = Exam()

        #test with bad xml and xml_none, which should yield verbatim html
        for xml in [badxml1, xml_none]:
            exam.xml_metadata = xml
            for i in range(10): #10 tests
                #build html with random number of questions
                j = random.randint(0,10)
                html = preamble
                for k in range(j):
                    html += question_template % k
                exam.html_content = html
                self.assertEqual(exam.getHTML(), {'html':html, 'subset':False, 'question_ids':[]})

        #random test with good xml and good html.  these cases should result in a subset
        for i in range(10): #10 tests
            n = random.randint(3,10) # number of actual questions
            exam.xml_metadata = xml_template % (n-2) #number of desired questions is n-2
            html = preamble
            for k in range(n):
                html += question_template % k
            exam.html_content = html
            result = exam.getHTML()
            self.assertTrue(result['subset'])
            self.assertEqual(len(result['question_ids']), n-2)
            #parse out which random numbers were chosen
            chosen_nums = map(lambda id: int(id[-1]), result['question_ids'])
            #now reconstuct html to test equivalence
            reconstructed_html = preamble
            for num in chosen_nums:
                reconstructed_html += question_template % num
            self.assertEqual(re.sub(r"\s","", result['html']), re.sub(r"\s","", reconstructed_html))

        #random test with good xml and good html with requesting more than we have.  these cases should not result in a subset
        for i in range(10): #10 tests
            n = random.randint(3,10) # number of actual questions
            exam.xml_metadata = xml_template % (n+2) #number of desired questions is n+2
            html = preamble
            for k in range(n):
                html += question_template % k
            exam.html_content = html
            result = exam.getHTML()
            self.assertFalse(result['subset'])
            self.assertEqual(len(result['question_ids']), n)
            self.assertEqual(re.sub(r"\s","", result['html']), re.sub(r"\s","", html))

        #test specifying question_ids
        for i in range(50): #50 tests
            n = 10 #10 questions
            #setup the html
            html = preamble
            for k in range(n):
                html += question_template % k
            exam.html_content = html
            exam.xml_metadata = xml_template % 20 #to show that the choosenquestions attr doesn't matter in this case
            
            if i==0: #no removal here
                chosen_nums = range(n)
            else:
                m = random.randint(0,9) # number of questions in question_ids, at most 9 so there will also be a removal
                t = range(2*n) #specify some qids that are not in the html
                chosen_nums = []
                while m != 0:
                    c = random.choice(t)
                    t.remove(c)
                    chosen_nums.append(c)
                    m -= 1

            chosen_ids = map(lambda n: "problem_%d" % n, chosen_nums)
            result = exam.getHTML(question_ids=chosen_ids)
            if i==0:
                self.assertFalse(result['subset'])
            else:
                self.assertTrue(result['subset'])
            correct_chosen_nums = filter(lambda num: num < n, chosen_nums)
            correct_chosen_nums.sort()
            correct_chosen_ids = map(lambda n: "problem_%d" % n, correct_chosen_nums)
            self.assertEqual(correct_chosen_ids, result['question_ids'])
            #reconstruct html to test html output
            reconstructed_html = preamble
            for num in correct_chosen_nums:
                reconstructed_html += question_template % num
            self.assertEqual(re.sub(r"\s","", result['html']), re.sub(r"\s","", reconstructed_html))

