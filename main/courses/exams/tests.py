# -*- coding: utf-8 -*-
# per http://www.python.org/peps/pep-0263.html

from nose.plugins.attrib import attr
import random
import re
from sets import Set

from django.test import TestCase

from courses.exams.autograder import *
from courses.exams.views import compute_penalties
from fake_remote_grader import *

@attr('slow')
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

    def test_numericresponse_metadata_errors(self):
        """
        Tests exceptions for numeric responses
        """
        xml1 = """
                <exam_metadata>
                <question_metadata id="problem_4" data-report="Short-answer2">
                    <response name="q4d" answertype="numericalresponse" answer="3.14159" data-report="Value of Pi"
                    correct-points="139" wrong-points="-23">
                        <responseparam type="tolerance" default=".02"></responseparam>
                    </response>
                    <response name="q4e" answertype="numericalresponse"
                    data-report="value of 502*9">
                        <responseparam type="tolerance" default="15%"></responseparam>
                    </response>
                    <response name="q4f" answertype="numericalresponse" answer="5" data-report="number of fingers on a hand"></response>
                </question_metadata>
                </exam_metadata>
              """
        xml2 = """
            <exam_metadata>
            <question_metadata id="problem_4" data-report="Short-answer2">
                <response name="q4d" answertype="numericalresponse" answer="3.1415b9" data-report="Value of Pi"
                correct-points="139" wrong-points="-23">
                    <responseparam type="tolerance" default=".02"></responseparam>
                </response>
            </question_metadata>
            </exam_metadata>
            """

        xml3 = """
            <exam_metadata>
            <question_metadata id="problem_4" data-report="Short-answer2">
                <response name="q4d" answertype="numericalresponse" answer="3.14159" data-report="Value of Pi"
                correct-points="139" wrong-points="-23">
                    <responseparam type="tolerance" default=".0b2"></responseparam>
                </response>
            </question_metadata>
            </exam_metadata>
            """

        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<response name="q4e"> has no specified answer.*'):
            ag = AutoGrader(xml1)
        
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<response name="q4d">, cannot convert answer to number.*'):
            ag = AutoGrader(xml2)

        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<response name="q4d">, cannot convert tolerance to number.*'):
            ag = AutoGrader(xml3)



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

    
    def test_resubmission_and_late_penalty(self):
        """Unit test for the discount function """
        def float_compare(a, b, tolerance=0.001):
            print "(%f, %f)" % (a,b)
            return  b * (1-tolerance) <= a and a <= b * (1+tolerance)
        
        #Only resub penalty
        self.assertTrue(float_compare(compute_penalties(100, 1, 0, False, 0), 100))
        self.assertTrue(float_compare(compute_penalties(100.0, 1, 0, False, 0), 100.0))
        self.assertTrue(float_compare(compute_penalties(100.0, 2, 15, False, 0), 85.0))
        self.assertTrue(float_compare(compute_penalties(100.0, 3, 15, False, 0), 72.25))
        self.assertTrue(float_compare(compute_penalties(100.0, 3, 150, False, 0), 0))
        #Only late penalty
        self.assertTrue(float_compare(compute_penalties(100.0, 1, 0, True, 50), 50.0))
        self.assertTrue(float_compare(compute_penalties(100.0, 1, 0, False, 50), 100.0))
        self.assertTrue(float_compare(compute_penalties(100.0, 1, 0, True, 150), 0))
        self.assertTrue(float_compare(compute_penalties(100.0, 1, 0, False, 150), 100.0))
        #Both penalties
        self.assertTrue(float_compare(compute_penalties(100.0, 2, 15, True, 50), 42.5))
        self.assertTrue(float_compare(compute_penalties(100.0, 3, 15, True, 50), 36.125))
        self.assertTrue(float_compare(compute_penalties(100.0, 3, 15, True, 150), 0))
        self.assertTrue(float_compare(compute_penalties(100.0, 3, 150, True, 50), 0))


    def test_regex_metadata_errors(self):
        """
            Tests exceptions for regex responses
        """
        xml1 = r"""
            <exam_metadata>
            <question_metadata id="problem_4" data-report="Short-answer2">
                <response name="q4d" answertype="regexresponse" correct-points="139" wrong-points="-23">
                </response>
            </question_metadata>
            </exam_metadata>
            """
        xml2 = r"""
            <exam_metadata>
            <question_metadata id="problem_4" data-report="Short-answer2">
                <response name="q4d" answertype="regexresponse" answer="\\(bbd" data-report="Value of Pi"
                correct-points="139" wrong-points="-23">
                </response>
            </question_metadata>
            </exam_metadata>
            """
        
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<response name="q4d"> has no specified answer.*'):
            ag = AutoGrader(xml1)
        
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<response name="q4d">, your regular expression could not be compiled.*'):
            ag = AutoGrader(xml2)

    def test_regex_responses(self):
        """
        Tests for regex response auto grading
        """
        xml = ur"""
            <exam_metadata>
                <question_metadata id="problem_4" data-report="Short-answer2">
                    <response name="q4d" answertype="regexresponse" answer="b" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
                <question_metadata id="problem_5" data-report="Short-answer3">
                    <response name="q5d" answertype="regexresponse" answer="\(\d*\)" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
                <question_metadata id="problem_6" data-report="Short-answer4">
                    <response name="q6d" answertype="regexresponse" answer="b" correct-points="139" wrong-points="-23">
                       <responseparam flag="IGNORECASE" />
                    </response>
                </question_metadata>
                <question_metadata id="problem_7" data-report="Short-answer5">
                    <response name="q7d" answertype="regexresponse" answer="\\cat" match="true" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
                <question_metadata id="problem_8" data-report="Short-answer6">
                    <response name="q8d" answertype="regexresponse" answer="\\cat" match="true" correct-points="139" wrong-points="-23">
                        <responseparam flag="IGNORECASE" />
                    </response>
                </question_metadata>
                <question_metadata id="problem_9" data-report="Short-answer7">
                    <response name="q9d" answertype="regexresponse" answer="^\([0-9b]*\)$" correct-points="139" wrong-points="-23">
                        <responseparam flag="IGNORECASE" />
                        <responseparam flag="MULTILINE" />
                    </response>
                </question_metadata>
                <question_metadata id="problem_10" data-report="Short-answer8">
                    <response name="q10d" answertype="regexresponse" match="true" answer="^\([0-9b&amp;是]*\)$" correct-points="139" wrong-points="-23">
                        <responseparam flag="IGNORECASE" />
                        <responseparam flag="MULTILINE" />
                        <responseparam flag="UNICODE" />
                    </response>
                </question_metadata>
                <question_metadata id="problem_11" data-report="Short-answer9">
                    <response name="q11d" answertype="regexresponse" answer="&quot;&amp;&lt;是" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
            </exam_metadata>
            """
        
        ag = AutoGrader(xml)
        #No flags, basic testing whether answer contains b
        self.assertTrue(ag.grade('q4d', "zbx")['correct'])
        self.assertTrue(ag.grade('q4d', "(90dbs)")['correct'])
        self.assertFalse(ag.grade('q4d', "(m)")['correct'])
        self.assertFalse(ag.grade('q4d', "")['correct'])
        
        #No flags, testing for special symbols and escaping with '\'
        self.assertTrue(ag.grade('q5d', "()")['correct'])
        self.assertTrue(ag.grade('q5d', "(5)")['correct'])
        self.assertTrue(ag.grade('q5d', "(523490)")['correct'])
        self.assertFalse(ag.grade('q5d', "(m)")['correct'])
        self.assertFalse(ag.grade('q5d', "(53m23)")['correct'])
        self.assertFalse(ag.grade('q5d', "(502")['correct'])
        self.assertFalse(ag.grade('q5d', "291)")['correct'])
    
        #IGNORECASE flag, testing whether answer contains b or B
        self.assertTrue(ag.grade('q6d', "bbx")['correct'])
        self.assertTrue(ag.grade('q6d', "(b90ds)")['correct'])
        self.assertTrue(ag.grade('q6d', "sBxd")['correct'])
        self.assertTrue(ag.grade('q6d', "(9Bds)")['correct'])
        self.assertFalse(ag.grade('q6d', "(m)")['correct'])
        self.assertFalse(ag.grade('q6d', "k*9dvj")['correct'])
        self.assertFalse(ag.grade('q6d', "")['correct'])

        #testing using `match` whether answer starts with \cat
        self.assertTrue(ag.grade('q7d', r"\catalog")['correct'])
        self.assertTrue(ag.grade('q7d', r"\catatonic")['correct'])
        self.assertTrue(ag.grade('q7d', r"\catalan(5)")['correct'])
        self.assertTrue(ag.grade('q7d', r"\cat")['correct'])
        self.assertFalse(ag.grade('q7d', r"a\cat")['correct'])
        self.assertFalse(ag.grade('q7d', r"catamaran")['correct'])
        self.assertFalse(ag.grade('q7d', r"\Catalan")['correct'])
        self.assertFalse(ag.grade('q7d', r"a\Catm")['correct'])
        self.assertFalse(ag.grade('q7d', r"a\concatentation")['correct'])
        self.assertFalse(ag.grade('q7d', r"")['correct'])

        #testing using `match` and IGNORECASE whether answer starts with \cAt
        self.assertTrue(ag.grade('q8d', r"\catalog")['correct'])
        self.assertTrue(ag.grade('q8d', r"\caTatonic")['correct'])
        self.assertTrue(ag.grade('q8d', r"\cAtalan(5)")['correct'])
        self.assertTrue(ag.grade('q8d', r"\Cat")['correct'])
        self.assertFalse(ag.grade('q8d', r"a\cat")['correct'])
        self.assertFalse(ag.grade('q8d', r"catamaran")['correct'])
        self.assertTrue(ag.grade('q8d', r"\Catalan")['correct'])
        self.assertFalse(ag.grade('q8d', r"a\Catm")['correct'])
        self.assertFalse(ag.grade('q8d', r"a\concatentation")['correct'])
        self.assertFalse(ag.grade('q8d', r"")['correct'])

        #testing with `search`, IGNORECASE and MULTILINE
        self.assertTrue(ag.grade('q9d', u"(5)")['correct'])
        self.assertTrue(ag.grade('q9d', u"(5bb1)\nagb")['correct'])
        self.assertTrue(ag.grade('q9d', u"agb\n(5bb1)")['correct'])
        self.assertTrue(ag.grade('q9d', u"agb\n\n(523B31)")['correct'])
        self.assertFalse(ag.grade('q9d', ur"a\cat")['correct'])
        self.assertFalse(ag.grade('q9d', u"(5c2)")['correct'])
        self.assertFalse(ag.grade('q9d', u"(5C2)")['correct'])
        self.assertFalse(ag.grade('q9d', u"")['correct'])
        self.assertFalse(ag.grade('q9d', u"k(5)")['correct'])
        self.assertFalse(ag.grade('q9d', u"agb\n4(5是bb1)")['correct'])
        self.assertFalse(ag.grade('q9d', u"agb\n(523B31)8")['correct'])

        #testing with `match`, IGNORECASE, UNICODE, MULTILINE
        self.assertTrue(ag.grade('q10d', u"(5)")['correct'])
        self.assertTrue(ag.grade('q10d', u"(5是)")['correct'])
        self.assertTrue(ag.grade('q10d', u"(5b&)")['correct'])
        self.assertTrue(ag.grade('q10d', u"(5b&b1是)\nagb")['correct'])
        self.assertFalse(ag.grade('q10d', u"agb\n(5B&b1)")['correct'])
        self.assertFalse(ag.grade('q10d', u"agb\n\n(523B31)")['correct'])
        self.assertFalse(ag.grade('q10d', ur"a\cat")['correct'])
        self.assertFalse(ag.grade('q10d', u"(5c是2)")['correct'])
        self.assertFalse(ag.grade('q10d', u"(5C2)")['correct'])
        self.assertFalse(ag.grade('q10d', u"")['correct'])
        self.assertFalse(ag.grade('q10d', u"k(5是)")['correct'])
        self.assertFalse(ag.grade('q10d', u"4(5bb1)\n3")['correct'])
        self.assertFalse(ag.grade('q10d', u"(523B31)8\n3220")['correct'])

        #special testing for how to encode invalid characters in the answer attribute
        #also test that the scores are not screwed up
        self.assertEqual(ag.grade('q11d', u'"&<是'), {'correct':True, 'score':139})
        self.assertEqual(ag.grade('q11d', u'"&<是3'), {'correct':True, 'score':139})
        self.assertEqual(ag.grade('q11d', u'5"&<是3'), {'correct':True, 'score':139})
        self.assertEqual(ag.grade('q11d', u'5"&<否3'), {'correct':False, 'score':-23})
        self.assertEqual(ag.grade('q11d', u'"&fam是k<3'), {'correct':False, 'score':-23})
    
    def test_string_metadata_errors(self):
        """
        Tests exceptions for string responses
        """
        xml1 = r"""
            <exam_metadata>
                <question_metadata id="problem_4" data-report="Short-answer2">
                    <response name="q4d" answertype="stringresponse" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
            </exam_metadata>
            """
        xml2 = r"""
            <exam_metadata>
                <question_metadata id="problem_5" data-report="Short-answer3">
                    <response name="q4e" answertype="stringresponse" answer="" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
            </exam_metadata>
            """
        
        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<response name="q4d"> has no specified answer.*'):
            ag = AutoGrader(xml1)

        with self.assertRaisesRegexp(AutoGraderMetadataException, '.*<response name="q4e"> has no specified answer.*'):
            ag = AutoGrader(xml2)

    def test_string_responses(self):
        """
            Tests string responses
        """
        xml = ur"""
            <exam_metadata>
                <question_metadata id="problem_4" data-report="Short-answer2">
                    <response name="q4d" answertype="stringresponse" answer="¡TheRightAnswer是!" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
                <question_metadata id="problem_5" data-report="Short-answer3">
                    <response name="q5d" answertype="stringresponse" answer="    ¡TheRightAnswer是!  " correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
                <question_metadata id="problem_6" data-report="Short-answer4">
                    <response name="q6d" answertype="stringresponse" answer="¡TheRightAnswer是!" ignorecase="true" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
                <question_metadata id="problem_7" data-report="Short-answer5">
                    <response name="q7d" answertype="stringresponse" answer="    ¡TheRightAnswer是!  " ignorecase="true" correct-points="139" wrong-points="-23">
                    </response>
                </question_metadata>
            </exam_metadata>
            """
        ag = AutoGrader(xml)
        #basic test, including unicode
        self.assertEqual(ag.grade("q4d", u"¡TheRightAnswer是!"),         {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q4d", u"    ¡TheRightAnswer是!  "),  {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q4d", u"¡therightanswer是!"),         {'correct':False, 'score':-23})
        self.assertEqual(ag.grade("q4d", u"TheWrongAnswer是!"),          {'correct':False, 'score':-23})
        #testing strip() in answer xml, including unicode
        self.assertEqual(ag.grade("q5d", u"¡TheRightAnswer是!"),         {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q5d", u"    ¡TheRightAnswer是!  "),  {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q5d", u"¡therightanswer是!"),         {'correct':False, 'score':-23})
        self.assertEqual(ag.grade("q5d", u"TheWrongAnswer是!"),          {'correct':False, 'score':-23})
        #case-insensitive test, including unicode
        self.assertEqual(ag.grade("q6d", u"¡TheRightAnswer是!"),         {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q6d", u"    ¡TheRightAnswer是!  "),  {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q6d", u"¡therightanswer是!"),         {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q6d", u"TheWrongAnswer是!"),          {'correct':False, 'score':-23})
        #case insensitive testing strip() in answer xml, including unicode
        self.assertEqual(ag.grade("q7d", u"¡TheRightAnswer是!"),         {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q7d", u"    ¡TheRightAnswer是!  "),  {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q7d", u"¡therightanswer是!"),         {'correct':True, 'score':139})
        self.assertEqual(ag.grade("q7d", u"TheWrongAnswer是!"),          {'correct':False, 'score':-23})

    

    ### INTERACTIVE AUTOGRADER ###

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

</exam_metadata>
"""

    def test_interactive_grader_required_elements(self):
        """Interactive grader requires some XML elements"""

        elements = ["database-file", "parameters", "select_dict", "answer-file"]
        for elem in elements:
            open_tag = "<" + elem + ">"
            close_tag = "</" + elem + ">"
            # re.S flag so the regexp can match newlines between elements
            partial_xml = re.sub("%s.*%s" % (open_tag, close_tag), 
                    "", self.interactive_xml, flags=re.S)
            with self.assertRaisesRegexp(AutoGraderMetadataException,
                    ".*A <%s> element is required" % elem):
                AutoGrader(partial_xml)


    def test_interactive_grader_basic(self):
        """
        Interactive autograder with fake remote endpoint (basic)

        Uses some XML from a db class interactive exercise, but the actual values
        aren't used since we just fake out the endpoint.

        The trick here is overriding the global method that urllib2 uses to open
        files.  You have to remember to restore urllib2 to a good state before 
        finishing though otherwise urllib2 will be horked.  Method cribbed from:
            http://stackoverflow.com/questions/2276689/how-do-i-unit-test-a-module-that-relies-on-urllib2

        Work for this is done in fake_remote_grader.py
        """

        ag = AutoGrader(self.interactive_xml)

        self.assertEqual(ag.points_possible, 2.0)
        self.assertEqual(len(ag.grader_functions), 2)

        # the feedback is opaque, so just carry that around
        fb = [{"user_answer": "user-input", "explanation": "grader-output", "score": 0}]
        fbstr = json.dumps(fb)

        with fake_remote_grader('{"score":0, "maximum-score":1, "feedback":%s}' % fbstr):
            g = ag.grade("q1b", "should_fail")
            self.assertEqual(g, {'correct': False, 'score': 0, 'feedback': fb})

        with fake_remote_grader('{"score":1, "maximum-score":1, "feedback":%s}' % fbstr):
            g = ag.grade("q1b", "should_succeed")
            self.assertEqual(g, {'correct': True, 'score': 1, 'feedback': fb})

        with fake_remote_grader('{"score":10, "maximum-score":10, "feedback":%s}' % fbstr):
            g = ag.grade("q1b", "should_succeed")
            self.assertEqual(g, {'correct': True, 'score': 1, 'feedback': fb})

            g = ag.grade("q2b", "should_succeed")
            self.assertEqual(g, {'correct': True, 'score': 1, 'feedback': fb})

        with fake_remote_grader('{"score":1, "feedback":%s}' % fbstr):
            g = ag.grade("q1b", "should_succeed")
            self.assertEqual(g, {'correct': True, 'score': 1, 'feedback': fb})

        with fake_remote_grader('{"score":0, "feedback":%s}' % fbstr):
            g = ag.grade("q1b", "should_fail")
            self.assertEqual(g, {'correct': False, 'score': 0, 'feedback': fb})


    def test_interactive_grader_unicode(self):
        """Interactive autograder with fake remote endpoint (unicode)"""

        ag = AutoGrader(self.interactive_xml)

        ascii_string = "ascii test string"
        unicode_string = u'娱乐资讯请点击'    # "click infotainment" from china.com homepage

        fb = [{"user_answer": "user-input", "explanation": "grader-output", "score": 0}]
        fbstr = json.dumps(fb)

        with fake_remote_grader('{"score":0, "feedback":%s}' % fbstr):
            g = ag.grade("q1b", ascii_string)
            self.assertEqual(g, {'correct': False, 'score': 0, 'feedback': fb})

        with fake_remote_grader('{"score":0, "feedback":%s}' % fbstr):
            g = ag.grade("q1b", unicode_string)
            self.assertEqual(g, {'correct': False, 'score': 0, 'feedback': fb})


    def test_interactive_bad_input(self):
        """Interactive autograder error handling, bad input

        The interactive autograder needs to handle all sorts of
        cases where the remote grader fails.  The right behavior
        is to retry until it can get a valid grade, and if it can't,
        give up instead of scoring a failure.
        """

        ag = AutoGrader(self.interactive_xml)

        # we've seen a sick grader time out like this -- shouldn't grade
        bad_return = r'{"score":0,"maximum-score":1,"feedback":[{"user_answer":"<result> {for $c1 in doc(\"countries.xml\")//country let $d1 := ($c1/@population div $c1/@area) for $c2 in doc(\"countries.xml\")//country let $d2:= ($c2/@population div $c2/@area) where $d1 >= $d2 return <highest density = \"{$d1}\">{data($c1/@name)} </highest>}  {for $c1 in doc(\"countries.xml\")//country let $d1 := ($c1/@population div $c1/@area) for $c2 in doc(\"countries.xml\")//country let $d2:= ($c2/@population div $c2/@area) where $d1 <= $d2 return <lowest density = \"{$d1}\">{data($c1/@name)} </lowest>} </result>","score":0,"explanation":"Timeout Error"}]}'
        with fake_remote_grader(bad_return):
            with self.assertRaises(AutoGraderGradingException):
                g = ag.grade("q1b", "should throw exception")

        # we've seen a sick grader time out like this too
        no_explanation_score0 = r'{"score":0, "maximum":1, "feedback":[{"explanation":""}]}'
        with fake_remote_grader(no_explanation_score0):
            with self.assertRaises(AutoGraderGradingException):
                g = ag.grade("q1b", "should throw exception")

        # but same thing with score=1 should be OK though (never penalize for no explanation)
        no_explanation_score1 = r'{"score":1.0, "maximum":1, "feedback":[{"explanation":""}]}'
        with fake_remote_grader(no_explanation_score1):
            g = ag.grade("q1b", "should be OK")
            self.assertEqual(g, {'correct': True, 'score': 1.0, 'feedback': [{"explanation": ""}] })


    def test_interactive_retries(self):
        """Interactive autograder error handling, retry logic"""

        fb = [{"user_answer": "user-input", "explanation": "grader-output", "score": 0}]
        fbstr = json.dumps(fb)
        ag = AutoGrader(self.interactive_xml)

        for i in range(3):
            # up to four attempts are allowed
            fails_allowed = i+1
            with fake_remote_grader_fails_n_times('{"score":0, "feedback":%s}' % fbstr, 
                    fails_allowed):
                g = ag.grade("q1b", "should eventually score, incorrectly")
                self.assertEqual(g, {'correct': False, 'score': 0, 'feedback': fb})

        with fake_remote_grader_fails_n_times('{"score":0, "feedback":%s}' % fbstr, 4):
            with self.assertRaises(AutoGraderGradingException):
                g = ag.grade("q1b", "should eventually score, incorrectly")
