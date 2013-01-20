# -*- coding: utf-8 -*-
# per http://www.python.org/peps/pep-0263.html

import random
import re
import urllib,urllib2
from django.test import TestCase
from django.conf import settings
from courses.exams.autograder import *
from sets import Set
from StringIO import StringIO

class SimpleTest(TestCase):
    def test_multiple_choice_factory_normal(self):
        """
        Tests the multiple-choice autograder.
        """
        ag = AutoGrader("__testing_bypass")
            #Regular test case
        mc_fn = ag._MC_grader_factory(["a","b"],correct_pts=15,wrong_pts=-3)
        self.assertEqual(mc_fn(["a","b"]),{'correct':True,'score':15,'correct_choices':{"a":True,"b":True}, 'wrong_choices':{}})
        self.assertTrue(mc_fn(("b","a"))['correct']) #note this input is a tuple
        self.assertTrue(mc_fn(("b","b","a","a"))['correct']) #and this one too
        self.assertEqual(mc_fn(["a","b","c"]), {'correct':False, 'score':-3, 'correct_choices':{"a":True,"b":True}, 'wrong_choices':{"c":'fp'}})
        self.assertEqual(mc_fn(["a"]), {'correct':False, 'score':-3, 'correct_choices':{"a":True}, 'wrong_choices':{"b":'fn'}})
        self.assertFalse(mc_fn([])['correct'])

    def test_multiple_choice_factory_empty(self):
        """
        Tests the multiple-choice autograder when initialized to empty list
        """
        ag = AutoGrader("__testing_bypass")
            #Empty case
        empty_fn = ag._MC_grader_factory([])
        self.assertTrue(empty_fn([])['correct'])
        self.assertFalse(empty_fn(["a"])['correct'])
        self.assertFalse(empty_fn(["a","b"])['correct'])

    def test_multiple_choice_factory_random(self):
        """
            Uses the random generator to make test cases for the multiple choice factory
            Tests 10 times
        """
        ag = AutoGrader("__testing_bypass")
        choicelist = "abcdefghijklmnopqrstuvwxyz"
        for i in range(10):
            numsolns = random.randint(1,26)
            solutions = random.sample(choicelist, numsolns)
            grader = ag._MC_grader_factory(solutions)
            wrongsub = random.sample(choicelist, random.randint(1,26))
            if Set(solutions) != Set(wrongsub):
                self.assertFalse(grader(wrongsub)['correct'])
            random.shuffle(solutions)
            self.assertTrue(grader(solutions)['correct'])

    def test_multiple_choice_metadata(self):
        """
        Tests basic functionality of multiple-choice input via metadata
        """
        xml = """
            <exam_metadata>
                <question_metadata id="problem_1" data-report="Apple Competitor Question">
                    <response name="q1d" answertype="multiplechoiceresponse" data-report="Apple Competitors" correct-points="15" wrong-points="-2">
                        <choice value="ipad" data-report="iPad" correct="false">
                            <explanation>Try again</explanation>
                        </choice>
                        <choice value="napster" data-report="Napster" correct="true">
                            <explanation>Try again</explanation>
                        </choice>
                        <choice value="ipod" data-report="iPod" correct="true">
                            <explanation>This is right!</explanation>
                        </choice>
                        <choice value="peeler" data-report="Vegetable Peeler" correct="false">
                            <explanation>Try again</explanation>
                        </choice>
                        <choice value="android" data-report="Android" correct="false">
                            <explanation>Try again</explanation>
                        </choice>
                        <choice value="beatles" data-report="The Beatles" correct="false">
                            <explanation>Try again</explanation>
                        </choice>
                    </response>
                </question_metadata>
                <question_metadata id="problem_2">
                    <response name="test2" answertype="multiplechoiceresponse">
                        <choice value="a" correct="False" />
                        <choice value="b" correct="True" />
                        <choice value="c" correct="True" />
                    </response>
                </question_metadata>
            </exam_metadata>
            """
        ag = AutoGrader(xml)
            #problem 1
        self.assertEqual(ag.grader_functions['q1d'](["napster", "ipod"]), {'correct':True, 'score':15, 'correct_choices':{'ipod':True,'napster':True}, 'wrong_choices':{}})
        self.assertTrue(ag.grader_functions['q1d'](["ipod", "napster"])['correct'])
        self.assertEqual(ag.grader_functions['q1d'](["ipad", "ipod", "napster"]), {'correct':False, 'score':-2, 'correct_choices':{'ipod':True, 'napster':True}, 'wrong_choices':{'ipad':'fp'}})
        self.assertFalse(ag.grader_functions['q1d'](["ipo"])['correct'])
        self.assertFalse(ag.grader_functions['q1d'](["ipod"])['correct'])
        self.assertFalse(ag.grader_functions['q1d']([])['correct'])
        self.assertTrue(ag.grade('q1d', ["ipod", "napster"])['correct'])
        self.assertFalse(ag.grade('q1d', ["q1d_1"])['correct'])

            #problem 2
        self.assertEqual(ag.grader_functions['test2'](["b","c"]),{'correct':True,'score':1, 'correct_choices':{'b':True, 'c':True}, 'wrong_choices':{}})
        self.assertTrue(ag.grader_functions['test2'](["c","b"])['correct'])
        self.assertEqual(ag.grader_functions['test2'](["a","b"]),{'correct':False,'score':0, 'correct_choices':{'b':True}, 'wrong_choices':{'a':'fp','c':'fn'}})
        self.assertFalse(ag.grader_functions['test2'](["a","b","c"])['correct'])
        self.assertFalse(ag.grader_functions['test2'](["a"])['correct'])
        self.assertFalse(ag.grader_functions['test2']([])['correct'])
        self.assertTrue(ag.grade('test2',["b","c"])['correct'])
        self.assertFalse(ag.grade('test2',["a"])['correct'])

            #exception due to using an undefined input name
        with self.assertRaisesRegexp(AutoGraderGradingException, 'Input/Response name="notDef" is not defined in grading template'):
            ag.grade('notDef', ['a','b'])


    def test_parse_xml_question_metadata_no_id(self):
        """Tests for exception when parsing question metadata with no id"""
        
        xml = """
            <exam_metadata>
            <question_metadata>
            </question_metadata>
            </exam_metadata>
            """
        with self.assertRaisesRegexp(AutoGraderMetadataException, 'A <question_metadata> tag has no "id" attribute!'):
            ag = AutoGrader(xml)


    def test_parse_xml_question_metadata_no_response(self):
        """Tests for exception when parsing question metadata with no responses"""
        
        xml = """
            <exam_metadata>
            <question_metadata id="q1">
            </question_metadata>
            </exam_metadata>
            """
        with self.assertRaisesRegexp(AutoGraderMetadataException, '<question_metadata id="q1"> has no <response> child tags!'):
            ag = AutoGrader(xml)

    def test_parse_xml_response_no_name(self):
        """Tests for exception when parsing response with no name"""
        
        xml = """
            <exam_metadata>
            <question_metadata id="q1">
                <response answertype="multiplechoiceresponse"/>
            </question_metadata>
            </exam_metadata>
            """
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*no name attribute.*'):
            ag = AutoGrader(xml)


    def test_parse_xml_question_response_no_type(self):
        """Tests for exception when parsing response with no answertype"""
        
        xml = """
            <exam_metadata>
            <question_metadata id="q1">
                <response name="foo" />
            </question_metadata>
            </exam_metadata>
            """
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*no "answertype" attribute.*'):
            ag = AutoGrader(xml)

    def test_parse_xml_question_dup_response(self):
        """
        Tests for exception when parsing XML with duplicate response names
        NOTE: This is not okay even across different questions.
        """
        
        xml = """
            <exam_metadata>
            <question_metadata id="q1">
                <response name="foo" answertype="multiplechoiceresponse">
                    <choice value="a" correct="true" />
                </response>
            </question_metadata>
            <question_metadata id="q2">
                <response name="foo" answertype="multiplechoiceresponse">
                    <choice value="a" correct="true" />
                </response>
            </question_metadata>
            </exam_metadata>
            """
        with self.assertRaisesRegexp(AutoGraderMetadataException, 'Duplicate name "foo".*<response>.*'):
            ag = AutoGrader(xml)


    def test_parse_xml_question_response_no_choices(self):
        """Tests for exception when parsing response with no choices"""
        
        xml = """
            <exam_metadata>
            <question_metadata id="q1">
                <response name="foo" answertype="multiplechoiceresponse" />
            </question_metadata>
            </exam_metadata>
            """
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*no <choice> descendants.*'):
            ag = AutoGrader(xml)

    def test_parse_xml_question_response_dup_choice(self):
        """
            Tests for exception when parsing response with duplicate choice id
            NOTE: it is okay to duplicate response ids across choices
        """
        
        xml = """
            <exam_metadata>
            <question_metadata id="q1">
                <response name="foo" answertype="multiplechoiceresponse">
                    <choice value="a" correct="true" />
                    <choice value="a" correct="false" />
                </response>
            </question_metadata>
            <question_metadata id="q2">
                <response name="foo2" answertype="multiplechoiceresponse">
                    <choice value="a" correct="true" />
                </response>
            </question_metadata>
            </exam_metadata>
            """
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<choice> tags with duplicate value "a"'):
            ag = AutoGrader(xml)

    def test_parse_xml_question_response_no_choice_id(self):
        """
        Tests for exception when parsing choice with no id
        """
        
        xml = """
              <exam_metadata>
              <question_metadata id="q1">
                  <response name="foo" answertype="multiplechoiceresponse">
                      <choice value="a" correct="true"></choice>
                      <choice correct="false"></choice>
                  </response>
              </question_metadata>
              </exam_metadata>
              """
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<choice> tag with no "value".*'):
            ag = AutoGrader(xml)

    def test_parse_numericresponse_metadata(self):
        """
        Testing driver for numerical response development
        """

        xml = """
            <exam_metadata>
            <question_metadata id="problem_4" data-report="Short-answer2">
                <response name="q4d" answertype="numericalresponse" answer="3.14159" data-report="Value of Pi" 
                          correct-points="139" wrong-points="-23">
                    <responseparam type="tolerance" default=".02"></responseparam>
                </response>
                <response name="q4e" answertype="numericalresponse" answer="4518"
                    data-report="value of 502*9">
                    <responseparam type="tolerance" default="15%"></responseparam>
                </response>
                <response name="q4f" answertype="numericalresponse" answer="5" data-report="number of fingers on a hand"></response>
            </question_metadata>
            </exam_metadata>
            """
        ag = AutoGrader(xml)
        self.assertEqual(ag.grade('q4d', "3.14159"), {'correct':True, 'score':139})
        self.assertTrue(ag.grade('q4d', str(3.14159+0.02))['correct'])
        self.assertTrue(ag.grade('q4d', str(3.14159-0.02))['correct'])
        self.assertEqual(ag.grade('q4d',"3.5"), {'correct':False,'score':-23})
        self.assertFalse(ag.grade('q4d',"3.0")['correct'])
    
        self.assertEqual(ag.grade('q4e', "4518"), {'correct':True, 'score':1})
        self.assertTrue(ag.grade('q4e', str(4518*1.149))['correct'])
        self.assertTrue(ag.grade('q4e', str(4518*0.851))['correct'])
        self.assertEqual(ag.grade('q4e',str(4518*1.151)), {'correct':False, 'score':0})
        self.assertFalse(ag.grade('q4e',str(4518*1.849))['correct'])

        self.assertTrue(ag.grade('q4f', "5")['correct'])
        self.assertFalse(ag.grade('q4f', "4")['correct'])
        self.assertFalse(ag.grade('q4f', "6")['correct'])

    def test_default_with_numericresponse_metadata(self):
        """
        Using the numerical response XML, test AutoGraders with that return "True" and "False" responses if no autograder is defined for a matching
        problemID
        """
        
        xml = """
            <exam_metadata>
            <question_metadata id="problem_4" data-report="Short-answer2">
            <response name="q4d" answertype="numericalresponse" answer="3.14159" data-report="Value of Pi"
            correct-points="139" wrong-points="-23">
            <responseparam type="tolerance" default=".02"></responseparam>
            </response>
            <response name="q4e" answertype="numericalresponse" answer="4518"
            data-report="value of 502*9">
            <responseparam type="tolerance" default="15%"></responseparam>
            </response>
            <response name="q4f" answertype="numericalresponse" answer="5" data-report="number of fingers on a hand"></response>
            </question_metadata>
            </exam_metadata>
            """
        #basic, copied over tests
        ag = AutoGrader(xml)
        self.assertEqual(ag.grade('q4d', "3.14159"), {'correct':True, 'score':139})
        self.assertTrue(ag.grade('q4d', str(3.14159+0.02))['correct'])
        self.assertTrue(ag.grade('q4d', str(3.14159-0.02))['correct'])
        self.assertEqual(ag.grade('q4d',"3.5"), {'correct':False,'score':-23})
        self.assertFalse(ag.grade('q4d',"3.0")['correct'])
        #exception due to using an undefined input name
        with self.assertRaisesRegexp(AutoGraderGradingException, 'Input/Response name="randomDNE" is not defined in grading template'):
            ag.grade('randomDNE', "33")


        agt = AutoGrader(xml, default_return=True)
        self.assertEqual(agt.grade('q4d', "3.14159"), {'correct':True, 'score':139})
        self.assertTrue(agt.grade('q4d', str(3.14159+0.02))['correct'])
        self.assertTrue(agt.grade('q4d', str(3.14159-0.02))['correct'])
        self.assertEqual(agt.grade('q4d',"3.5"), {'correct':False,'score':-23})
        self.assertFalse(agt.grade('q4d',"3.0")['correct'])
        self.assertTrue(agt.grade('randomDNE',"33")['correct']) #This is the actual test

        agf = AutoGrader(xml, default_return=False)
        self.assertEqual(agf.grade('q4d', "3.14159"), {'correct':True, 'score':139})
        self.assertTrue(agf.grade('q4d', str(3.14159+0.02))['correct'])
        self.assertTrue(agf.grade('q4d', str(3.14159-0.02))['correct'])
        self.assertEqual(agf.grade('q4d',"3.5"), {'correct':False,'score':-23})
        self.assertFalse(agf.grade('q4d',"3.0")['correct'])
        self.assertFalse(agf.grade('randomDNE',"33")['correct']) #This is the actual test


    ### INTERACTIVE AUTOGRADER ###

    def test_interactive_grader_required_elements(self):
        """Interactive grader requires some XML elements"""

        valid_xml="""
<exam_metadata>
    <question_metadata id="q1" data-report="q1">
        <solution></solution>
        <response name="q1b" answertype="dbinteractiveresponse">
            <grader_name>SQL_Grader_schroot</grader_name>
            <database-file>sql-social-query2.db</database-file>
            <answer-file>sql-social-query-ans2.txt</answer-file>
            <select_dict></select_dict>
            <parameters>
                <qnum>1</qnum>
                <answer-text>Enter your SQL query here</answer-text>
            </parameters>
        </response>
    </question_metadata>
</exam_metadata>"""

        elements = ["database-file", "parameters", "select_dict", "answer-file"]
        for elem in elements:
            open_tag = "<" + elem + ">"
            close_tag = "</" + elem + ">"
            # re.S flag so the regexp can match newlines between elements
            partial_xml = re.sub("%s.*%s" % (open_tag, close_tag), "", valid_xml, flags=re.S)
            with self.assertRaisesRegexp(AutoGraderMetadataException,
                    ".*A <%s> element is required" % elem):
                AutoGrader(partial_xml)


    # Helper Methods

    def fake_remote_grader(self, answer):
        """Helper function for the interactive grader, override the remote
        grader to return the answer string provided."""

        def fake_remote_grader(req):
            grader_endpoint = getattr(settings, 'GRADER_ENDPOINT', 'localhost')
            if req.get_full_url() == grader_endpoint:
                resp = urllib2.addinfourl(StringIO(answer), "", req.get_full_url())
                resp.code = 200
                resp.msg = ""
                return resp

        class FakeGraderHTTPHandler(urllib2.HTTPHandler):
            def http_open(self, req):
                return fake_remote_grader(req)

        my_opener = urllib2.build_opener(FakeGraderHTTPHandler)
        urllib2.install_opener(my_opener)

    def restore_urllib2(self):
        default_opener = urllib2.build_opener(urllib2.HTTPDefaultErrorHandler)
        urllib2.install_opener(default_opener)


    def test_interactive_grader_basic(self):
        """
        Interactive autograder with fake remote endpoint (basic)

        Uses some XML from a db class interactive exercise, but the actual values
        aren't used since we just fake out the endpoint.

        The trick here is overriding the global method that urllib2 uses to open
        files.  You have to remember to restore urllib2 to a good state before 
        finishing though otherwise urllib2 will be horked.  Method cribbed from:
            http://stackoverflow.com/questions/2276689/how-do-i-unit-test-a-module-that-relies-on-urllib2
        """

        interactive_xml = """
<exam_metadata>

    <question_metadata id="q1" data-report="q1">
        <solution></solution>
        <response name="q1b" answertype="dbinteractiveresponse">
            <grader_name>SQL_Grader_schroot</grader_name>
            <database-file>sql-social-query2.db</database-file>
            <answer-file>sql-social-query-ans2.txt</answer-file>
            <select_dict></select_dict>
            <parameters>
                <qnum>1</qnum>
                <answer-text>Enter your SQL query here</answer-text>
            </parameters>
        </response>
    </question_metadata>

    <question_metadata id="q2" data-report="q2">
        <solution></solution>
        <response name="q2b" answertype="dbinteractiveresponse">
            <grader_name>SQL_Grader_schroot</grader_name>
            <database-file>sql-social-query2.db</database-file>
            <answer-file>sql-social-query-ans2.txt</answer-file>
            <select_dict></select_dict>
            <parameters>
                <qnum>2</qnum>
                <answer-text>Enter your SQL query here</answer-text>
            </parameters>
        </response>
    </question_metadata>

</exam_metadata>"""

        ag = AutoGrader(interactive_xml)

        self.assertEqual(ag.points_possible, 2.0)
        self.assertEqual(len(ag.grader_functions), 2)

        # the feedback is opaque, so just carry that around
        fb = [{"user_answer": "user-input", "explanation": "grader-output", "score": 0}]
        fbstr = json.dumps(fb)

        self.fake_remote_grader('{"score":0, "maximum-score":1, "feedback":%s}' %fbstr)
        self.assertEqual(ag.grade("q1b", "should_fail"),
                {'correct': False, 'score': 0, 'feedback': fb})

        self.fake_remote_grader('{"score":1, "maximum-score":1, "feedback":%s}' %fbstr)
        self.assertEqual(ag.grade("q1b", "should_succeed"),
                {'correct': True, 'score': 1, 'feedback': fb})

        self.fake_remote_grader('{"score":10, "maximum-score":10, "feedback":%s}' %fbstr)
        self.assertEqual(ag.grade("q1b", "should_succeed"),
                {'correct': True, 'score': 1, 'feedback': fb})
        self.assertEqual(ag.grade("q2b", "should_succeed"),
                {'correct': True, 'score': 1, 'feedback': fb})

        self.fake_remote_grader('{"score":1, "feedback":%s}' %fbstr)
        self.assertEqual(ag.grade("q1b", "should_succeed"),
                {'correct': True, 'score': 1, 'feedback': fb})

        self.fake_remote_grader('{"score":0, "feedback":%s}' %fbstr)
        self.assertEqual(ag.grade("q1b", "should_fail"),
                {'correct': False, 'score': 0, 'feedback': fb})

        self.restore_urllib2()


    def test_interactive_grader_unicode(self):
        """
        Interactive autograder with fake remote endpoint (unicode)
        """

        interactive_xml = """
<exam_metadata>
    <question_metadata id="q1" data-report="q1">
        <solution></solution>
        <response name="q1b" answertype="dbinteractiveresponse">
            <grader_name>SQL_Grader_schroot</grader_name>
            <database-file>sql-social-query2.db</database-file>
            <answer-file>sql-social-query-ans2.txt</answer-file>
            <select_dict></select_dict>
            <parameters>
                <qnum>1</qnum>
                <answer-text>Enter your SQL query here</answer-text>
            </parameters>
        </response>
    </question_metadata>
</exam_metadata>"""
        ag = AutoGrader(interactive_xml)

        ascii_string = "ascii test string"
        unicode_string = u'娱乐资讯请点击'    # "click infotainment" from china.com homepage

        fb = [{"user_answer": "user-input", "explanation": "grader-output", "score": 0}]
        fbstr = json.dumps(fb)

        self.fake_remote_grader('{"score":0, "feedback":%s}' %fbstr)
        self.assertEqual(ag.grade("q1b", ascii_string),
            {'correct': False, 'score': 0, 'feedback': fb})

        self.fake_remote_grader('{"score":0, "feedback":%s}' %fbstr)
        self.assertEqual(ag.grade("q1b", unicode_string),
            {'correct': False, 'score': 0, 'feedback': fb})

        self.restore_urllib2()
