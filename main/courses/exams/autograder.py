import re
from xml.dom.minidom import parseString

class AutoGrader():
    """
    Autograder for an entire pset here.
    Can be use to grade single problems, of course.
    """
    
    def __unicode__(self):
        graders=[]
        for k,v in self.grader_functions.iteritems():
            graders.append(k)
        return "AutoGrader functions for responses with names: %s " % (", ".join(sorted(graders)))
    
    def __init__(self, xml):
        if xml == "__testing_bypass":
            return 
        self.metadata_xml = xml #The XML metadata for the entire problem set.
        self.metadata_dom = parseString(xml) #The DOM corresponding to the XML metadata
        self.grader_functions={} #This is a dict that is keyed on the "name" of the submission (the input field) whose
                                 #value is a grader for that submission.

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
                    #more types should follow
            
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

        self.grader_functions[resp_name] = self._MC_grader_factory(answer_list)


    def _MC_grader_factory(self, answer_list):
        """
        A factory for returning multiple-choice graders.
        The signature of the returned function is 
            
            grader_fn(submission_iterable)
            
        submission_iterable is an iterable which has as each entry a string of of the name corresponding to a
        student submitted choice.  All correct choices must be selected, and no incorrect choice selected.
        """
        def grader_fn(submission_iterable):
            for sub in submission_iterable:
                if sub not in answer_list:
                    return False
            for ans in answer_list:
                if ans not in submission_iterable:
                    return False
            return True

        return grader_fn
            
    ########## Numeric response section ############

    def _parse_num(self, response_elem, resp_name, qid):
        """
        Parses each <response answertype="numericalresponse"> element
        and sets up its grader function
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

        self.grader_functions[resp_name] = self._NUM_grader_factory(answer, tolerance)
                    
    def _NUM_grader_factory(self, answer, tolerance):
        """
        Factory function for a numeric grader.  The signature of the grader_fn is
        
            grader_fn(submission)
            
        which returns True if answer-tolerance <= submission <= answer+tolerance, else returns False
        """
        def grader_fn(submission):
            return answer-tolerance <= submission and submission <= answer+tolerance

        return grader_fn
                    
    def grade(self, input_name, submission):
        """Grades student submission for response name=input_name"""
        if input_name not in self.grader_functions:
            raise AutoGraderGradingException('Input/Response name="%s" is not defined in grading template' % input_name)
        return self.grader_functions[input_name](submission)

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