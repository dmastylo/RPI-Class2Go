import re, collections
import urllib,urllib2
import json
import logging
from datetime import datetime

from django.conf import settings
from django.utils import encoding

from xml.dom.minidom import parseString


logger = logging.getLogger(__name__)

class AutoGrader():
    """
    Autograder for an entire pset here.
    Can be use to grade single problems, of course.
    """
    __true_default =  {'correct':True, 'score':0}
    __false_default = {'correct':False, 'score':0}

    def __unicode__(self):
        graders=[]
        for k,v in self.grader_functions.iteritems():
            graders.append(k)
        return "AutoGrader functions for responses with names: %s.  Total Possible Points: %s" % \
            (", ".join(sorted(graders)), str(self.points_possible))
    
    def __init__(self, xml, default_return=None):
        """
            
        Initializes the autograder.  Takes in one argument, xml, which represents the metadata_xml.
        default_return is a kwarg which can be (None (default), True, False), which specifies the behavior of the
        grader when 
            
        """
        self.points_possible=0.0
        
        if xml == "__testing_bypass":
            return

        def return_true_default():
            def tempFn(submission):
                return self.__true_default
            return tempFn
                
        def return_false_default():
            def tempFn(submission):
                return self.__false_default
            return tempFn
    
        self.metadata_xml = xml #The XML metadata for the entire problem set.
        self.metadata_dom = parseString(xml) #The DOM corresponding to the XML metadata

        if default_return is None:
            self.grader_functions = {} #This is a dict that is keyed on the "name" of the submission (the input field) whose
                                       #value is a grader function for that submission.
                                       #will throw an exception if the key (questionID) is not found
        elif default_return:
            self.grader_functions = collections.defaultdict(return_true_default)  #Returns true if key not found
        else:
            self.grader_functions = collections.defaultdict(return_false_default) #Returns false if key not found
                                 

        questions = self.metadata_dom.getElementsByTagName('question_metadata')
        for q in questions:
            self._parse_question_metadata(q)
    
    def _parse_question_metadata(self, question_elem):
        """parses <question_metadata> elements, delegating each <response> child"""
        
        qid = question_elem.getAttribute('id').strip()
        if qid == "":
            raise AutoGraderMetadataException('A <question_metadata> tag has no "id" attribute!')
        
        responses = question_elem.getElementsByTagName('response')
        if not responses:
            raise AutoGraderMetadataException('<question_metadata id="%s"> has no <response> child tags!' % qid)
    
        for resp in responses:
            resp_name = self._validate_resp(resp, qid) #validate first
            
            type = resp.getAttribute('answertype').strip()
            if type == "":
                raise AutoGraderMetadataException('A <response> tag (child of <question_metadata id="%s">) has no "answertype" attribute!' % qid)
            elif type == "multiplechoiceresponse":
                self._parse_mc(resp, resp_name, qid)
            elif type == "numericalresponse":
                self._parse_num(resp, resp_name, qid)
            elif type == "dbinteractiveresponse":
                self._parse_interactive(resp, resp_name, qid)
            # more types should follow
            
    def _validate_resp(self, response_elem, qid):
        """
        Helper function that validates that <response> elements have unique "name" attributes
        """
        resp_name = response_elem.getAttribute("name").strip()
        if resp_name == "":
            raise AutoGraderMetadataException('A <response> tag (child of <question_metadata id="%s">) has no name attribute!' % qid)
        
        if resp_name in self.grader_functions:
            raise AutoGraderMetadataException('Duplicate name "%s" found for multiple <response> tags.  One is a child of <question_metadata id="%s">' \
                                              % (resp_name, qid))
        return resp_name
             
        
    
    def _get_numeric_attribute_with_default(self, element, attribute, default=0.0):
        """
        Helper function that gets an attribute with a numeric value and returns the float numeric value.
        Throws exception if attribute is not convertible.
        Returns default if attribute is not set
        """
        str_val = element.getAttribute(attribute)
        if str_val == "": #default
            return default
        else:
            try:
                return float(str_val)
            except ValueError:
                raise AutoGraderMetadataException('Element %s has attribute %s that cannot be converted a number' % (str(element), attribute))

    
    ########## Multiple-choice section ############

    def _parse_mc(self, response_elem, resp_name, qid):
        """
        Parses each <response answertype="multiplechoiceresponse"> element
        and sets up its grader function
        """
        
        #build up the correct answers
        choices = response_elem.getElementsByTagName('choice')
        if not choices:
            raise AutoGraderMetadataException('<question_medata id="%s">, <response name="%s"> has no <choice> descendants' % (qid,resp_name))

        choice_list = [] # This list is really for validation only
        answer_list = [] # This list will build the grader function
        for c in choices:
            cid = c.getAttribute('value').strip()
            if cid == "":
                raise AutoGraderMetadataException('<question_metadata id="%s">, <response name="%s"> has descendant <choice> tag with no "value" attribute' \
                                                  % (qid, resp_name))
            if cid in choice_list:
                raise AutoGraderMetadataException('<question_metadata id="%s">, <response name="%s"> has descendant <choice> tags with duplicate value "%s"' \
                                                  % (qid, resp_name, cid))
            choice_list.append(cid)
                    
            if c.getAttribute('correct').strip().lower() == 'true':
                answer_list.append(cid)

        correct_pts = self._get_numeric_attribute_with_default(response_elem,'correct-points',1)
        wrong_pts = self._get_numeric_attribute_with_default(response_elem, 'wrong-points',0)

        self.points_possible += correct_pts
                    
        self.grader_functions[resp_name] = self._MC_grader_factory(answer_list, correct_pts=correct_pts, wrong_pts=wrong_pts)


    def _MC_grader_factory(self, answer_list, correct_pts=1, wrong_pts=0):
        """
        A factory for returning multiple-choice graders.
        The signature of the returned function is 
            
            {'correct':boolean, 'score':float, 'correct_choices':dict, 'wrong_choices':dict} = grader_fn(submission_iterable)

        submission_iterable is an iterable which has as each entry a string of of the name corresponding to a
        student submitted choice.  All correct choices must be selected, and no incorrect choice selected.
        The return value is a dict with keys 'correct' and 'score' (using dict to be future proof)
        'correct_choices' is a dict whose keys are all the correct choices selected by the student.
        'wrong_choices' is a dict whose keys are all the 'wrong' choices for the student, and whose value is either
            'fp' (false_positive) where the student selected a wrong answer, or 'fn', where the student did not select a right answer.
            
        """
        def grader_fn(submission_iterable):
            correct=True
            cc = {}
            wc = {}
            for sub in submission_iterable:
                if sub not in answer_list:
                    wc[sub]='fp'
                    correct=False
                else:
                    cc[sub]=True
            for ans in answer_list:
                if ans not in submission_iterable:
                    wc[ans]='fn'
                    correct=False
            points = correct_pts if correct else wrong_pts
            return {'correct':correct, 'score':points, 'correct_choices':cc, 'wrong_choices':wc}

        return grader_fn
            

    ########## Numeric response section ############

    def _parse_num(self, response_elem, resp_name, qid):
        """
        Parses each <numericalresponse> element and sets up its grader function
        """

        answer_str = response_elem.getAttribute("answer")
        
        if answer_str == "" :
            raise AutoGraderMetadataException('<question_medata id="%s">, <response name="%s"> has no specified answer' % (qid,resp_name))

        try:
            answer = float(answer_str)
        except ValueError:
            raise AutoGraderMetadataException('In <question_medata id="%s">, <response name="%s">, cannot convert answer to number' % (qid,resp_name))

        tolerance_str = ""
        
        children = response_elem.childNodes
        for node in children:
            if node.nodeType == node.ELEMENT_NODE and node.nodeName == "responseparam" and node.getAttribute('type') == "tolerance" :
                tolerance_str = node.getAttribute("default").strip()
                break #only consider first tolerance setting 

        tolerance = (0.001)*answer #default tolerance is 0.1% of answer
        if tolerance_str :
            try:
                if tolerance_str[-1] == "%" : #entered as a percentage
                    tolerance_grp = re.match(r"^(.*)%$", tolerance_str)
                    tolerance = float(tolerance_grp.group(1))/100*answer #ugly syntax--group(1)--to get matched substring out
                else:
                    tolerance = float(tolerance_str)
            except ValueError:
                raise AutoGraderMetadataException('In <question_medata id="%s">, <response name="%s">, cannot convert tolerance to number' % (qid,resp_name))

        correct_pts = self._get_numeric_attribute_with_default(response_elem,'correct-points',1)
        wrong_pts = self._get_numeric_attribute_with_default(response_elem, 'wrong-points',0)

        self.points_possible += correct_pts

        self.grader_functions[resp_name] = self._NUM_grader_factory(answer, tolerance, correct_pts=correct_pts, wrong_pts=wrong_pts)
                    
    def _NUM_grader_factory(self, answer, tolerance, correct_pts=1, wrong_pts=0):
        """
        Factory function for a numeric grader.  The signature of the grader_fn is
        
            {'correct':boolean, 'score':float} = grader_fn(submission)
            
        which returns True if answer-tolerance <= submission <= answer+tolerance, else returns False
        Submission is a string that gets converted to a float.
        The return value dict of with keys 'correct' and 'score' (using dict to be future proof)

        """
        def grader_fn(submission):
            try:
                sub_num = float(submission)
            except ValueError:
                raise AutoGraderGradingException("Your submission could not be converted to a number!")
            if answer-tolerance <= sub_num and sub_num <= answer+tolerance:
                return {'correct':True, 'score':correct_pts}
            else:
                return {'correct':False, 'score':wrong_pts}
        return grader_fn
                    

    ########## Interactive Exercise Grader ############

    def _parse_interactive(self, response_elem, resp_name, qid):
        """
        Reads a set of XML parameters that are passed along to a
        custom grader for the DB Class.  An example:

            <response name="sql1" answertype="dbclass-interactive">
                <grader_name>SQL_Grader_schroot</grader_name>
                <select_dict></select_dict>
                <database-file>sql-movies-query28.db</database-file>
                <answer-file>movie-query-ans8.txt</answer-file>
                <parameters>
                    <qnum>1</qnum>
                </parameters>
                <type>db_class</type>
            </response>

        The DB Class interactive grader expects to see a POST with
        a specific set of elements in the requests.  There are three
        direct elements:
            grader_name
            select_dict
            student_input

        and then an arbitrary set of elements called 'param[X]'.  
        student_input is filled in by the grader function later; we 
        populate the rest from the XML here.
        """
        response_nodes_found = []
        required_nodes = ["grader_name", "select_dict", "database-file", "answer-file", "parameters"]
        grader_post_params = {}
        for response_child in response_elem.childNodes:
            if response_child.nodeName == "#text":            # ignore
                next
            elif response_child.nodeName == "parameters":     # params are special
                response_nodes_found.append(response_child.nodeName)
                for pnode in response_child.childNodes:
                    key = "params[%s]" % pnode.nodeName
                    if pnode.childNodes.length:
                        val = pnode.childNodes[0].nodeValue
                        grader_post_params[key] = val
            else:                                             # all else becomes a post param
                response_nodes_found.append(response_child.nodeName)
                val = ""
                if response_child.childNodes.length:
                    val = response_child.childNodes[0].nodeValue
                grader_post_params[response_child.nodeName] = val
                
        for req in required_nodes: 
            if req not in response_nodes_found:
                response_node_id = response_elem.getAttribute('name').strip()
                raise AutoGraderMetadataException("Error in response node \"%s\": A <%s> element is required" 
                        % (response_node_id, req))

        self.points_possible += 1.0 ## DB exercises are worth 1 point, hardcoded
        self.grader_functions[resp_name] = self._INTERACTIVE_grader_factory(grader_post_params)

    def _INTERACTIVE_grader_factory(self, post_params):
        """
        Factory function for an interactive grader.  The signature of the grader_fn is

            {'correct':boolean, 'score':float, 'feedback':string } = grader_fn(submission)

        This does the remote call to the interactive grader and interprets the response.
        The grader returns a JSON structure that looks like this.

            {"score":0,
            "maximum-score":1,
            "feedback":[
                {"user_answer":"select * from movies",
                "score":0,
                "explanation":"<br><font style=\"color:red; font-weight:bold;\">Incorrect<\/font>..."
                }]
            }
        """

        def grader_fn(submission):
            """Grade an interactive exam by calling a remote grader."""

            def external_grader_request(grader_url, post_params):
                """Hit external grader endpoint.  TODO: add retry logic, here or in frontend (#1730)."""
                grader_timeout = 45    # seconds
                try:
                    post_data = urllib.urlencode(post_params)
                    time_before = datetime.now()
                    grader_conn = urllib2.urlopen(grader_url, post_data, grader_timeout)
                    time_after = datetime.now()
                    duration = time_after - time_before  # timedelta
                    logger.info("interactive grader returned in %s " % str(duration))
                except urllib2.HTTPError as e:
                    raise AutoGraderGradingException("Interactive grader HTTP error: %s" % str(e))
                except urllib2.URLError as e:
                    raise AutoGraderGradingException("Interactive grader connection error: %s" % str(e))

                try:
                    graded_result = grader_conn.read()
                except IOError as e:
                    raise AutoGraderGradingException("Interactive grader IO error: %s", str(e))
                except OSError as e:
                    raise AutoGraderGradingException("Interactive grader OS error: %s", str(e))
                if graded_result == "ERROR":
                    raise AutoGraderGradingException("Interactive grader internal problem (returned \"%s\")" % graded_result)

                return graded_result

            # grader_fn() body
            # default responses, to be overriden by what we actually got back
            response = {}
            response['correct'] = False
            response['score'] = 0
            response['feedback'] = ""

            # external grader can't handle unicode (see #1904) so just flatten to ascii
            ascii_submission = encoding.smart_str(submission, encoding='ascii', errors='ignore')
            post_params['student_input'] = ascii_submission

            # call remote grader
            logger.debug("External grader call: %s" % str(post_params))
            grader_url = getattr(settings, 'GRADER_ENDPOINT', 'localhost')
            graded_result = external_grader_request(grader_url, post_params)
            try:
                graded = json.loads(graded_result)
            except ValueError as e:
                raise AutoGraderGradingException("Error parsing interactive grader result: %s" % str(graded_result))
            except TypeError as e:
                raise AutoGraderGradingException("Unexpected type in interactive grader: %s" % str(graded_result))

            # interpret what we got from the grader
            # class2go just has one float score, coursera used score vs max, convert here
            if 'score' in graded:
                if 'maximum-score' in graded and graded['maximum-score'] != 0:
                    maxscore = float(graded['maximum-score'])
                else:
                    maxscore = 1.0
                if float(graded['score']) == maxscore:
                    response['correct'] = True
                response['score'] = float(graded['score']) / maxscore
            if 'feedback' in graded:
                response['feedback'] = graded['feedback']

            return response

        return grader_fn


    ########## The actual grader, for what it is ############

    def grade(self, input_name, submission):
        """Grades student submission for response name=input_name"""
        try:
            return self.grader_functions[input_name](submission)
        except KeyError:
            raise AutoGraderGradingException('Input/Response name="%s" is not defined in grading template' % input_name)

class AutoGraderException(Exception):
    """Base class for exceptions in this module"""
    pass

class AutoGraderMetadataException(AutoGraderException):
    """
    An error during the parsing/grading function generation step
    of the problemset XML metadata.  Could be because certain required attibutes or tags are missing.
    """
    pass
       
class AutoGraderGradingException(AutoGraderException):
    """
    An error during the auto grading step (not XML parsing or grading function generation)
    """
    pass

