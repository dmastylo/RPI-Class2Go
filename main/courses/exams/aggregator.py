from c2g.models import ExamRecord, Exam, ExamScore, ExamRecordScore, Course, CourseStudentScore, ContentGroup
from django.db.models import Q

import math
import collections
import re
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)


class ScoreAggregator():
    """ This class aggregates student scores on all exams in a course, primarily
        for the purpose of course grade assignment.
    """
    #These are the python names a written formula is allowed to reference.
    #Inspiration from http://lybniz2.sourceforge.net/safeeval.html
    #Note that anything in the math package is referenceable with the math package prefix
    #Hopefully all of these are pure functions with no side-effects, but I don't
    #have a formal proof using operational semantics :-P
    
    var_re = re.compile(r'{{\s*[-\w]+\s*}}', re.UNICODE)
    
    default_formula_obj = {'str':'', 'var_patterns':[], 'vars':[], 'max_points':0}
    
    safe_dict = {'math':math, 'abs':abs, 'divmod':divmod, 'len':len, 'max':max, 'min':min,
        'pow':pow, 'range':range, 'sum':sum, 'map':map, 'filter':filter, 'reduce':reduce, 'list':list}
    
    reserved_names = ['__student']

    def __init__(self, course, formulas={}):
        """
            This function instantiates the aggregator with a course <course> and 
            a dict of where keys are tags and values are formulas, as defined below.
            <course> MUST be a READY-MODE course.
            """
        self.course = course
        self.formulas = collections.defaultdict(lambda: self.default_formula_obj) #initialize instance variable
        for tag, formula in formulas.iteritems():
            self.add_formula(tag, formula)

    def add_formula(self, tag, formula):
        """
            <formula> is a string written in a domain-specific language built on
            django templating and python.  Basically, formula should be a python
            expression that evaluates to a number, with function names in python syntax
            e.g. max(), min(), math.floor().  A variable namespace corresponding to
            student grades on individual assessments is also provided via a django
            template language syntax.  For example, {{exam1}} refers to the student's
            ExamScore on the Exam with slug==exam1.  So an example formula would be
            'max({{exam1a}} ,{{exam1b}})*0.5 + {{exam2}}*0.5'
        """
        self.formulas[tag] = deepcopy(self.default_formula_obj)
        self.formulas[tag]['str'] = formula
        #get a list variables used in the formula, so we can look them up
        vars_patterns = self.var_re.findall(formula)
        vars = map(lambda li: li[2:-2].strip(), vars_patterns)  #yeah yeah, hardcoding.  django templates does it too
        self.formulas[tag]['vars_patterns'] = vars_patterns
        self.formulas[tag]['vars'] = vars
        self.formulas[tag]['max_points'] = self._fill_max_points(tag)
        
        #now we try out the formula_vars to make sure they're all Exam slugs in the course
        for var in vars:
            try:
                Exam.objects.get(course=self.course, slug=var)
            except Exam.DoesNotExist:
                if var in self.reserved_names:
                    continue
                else:
                    raise AggregatorFormulaVariableError("{{%s}} is not an assessment item in Course %s" % (var, course))
        
        #now try out the formula with all variables filled in a 0's, to see if we throw any errors
        #score_dict will become the template context
        #set entire context to return 0
        score_dict = collections.defaultdict(lambda:0)
        #do reserved names
        score_dict = self.fill_reserved_word_context(score_dict)
        
        formula_filled = self.fill_formula(tag, score_dict)
        print "%s: %s" % (tag, formula)

        #if there's a problem, this eval will raise an exception that will get passed on (no try...except here)
        self.eval_helper(formula_filled)

        

    def __unicode__(self):
        return "Aggregator formulas for %s with tags: %s" % (unicode(self.course), ", ".join(self.formulas.keys()))


    def fill_reserved_word_context(self, context, student_name="student"):
        context['__student'] = '"""%s"""' % student_name
        return context

    def max_points(self, tag):
        print("%s: %1.2f" % (tag, self.formulas[tag]['max_points']))
        return self.formulas[tag]['max_points']

    def _fill_max_points(self, tag):
        exams = Exam.objects.filter(course=self.course, is_deleted=False, slug__in=self.formulas[tag]['vars'])
        points_dict = collections.defaultdict(lambda:0)
        for exam in exams:
            points_dict[exam.slug] = exam.get_total_score()
        #do reserved names
        points_dict = self.fill_reserved_word_context(points_dict)

        formula = self.fill_formula(tag, points_dict)
        pts = self.eval_helper(formula)
        print("%s: MAX-POINTS: %1.2f" % (tag,pts))
        return pts

    def fill_formula(self, tag, context):
        """Fill out the formula pattern with context dict"""
        formula = self.formulas[tag]['str']
        for var in self.formulas[tag]['vars']:
            patt = r'{{\s*%s\s*}}' % re.escape(var)
            formula = re.sub(patt, str(context[var]), formula)
        return formula
    
    def aggregate(self, student, tags=None, writeDB=False):
        """
            This function aggregates the <student>'s scores on assessments in self.course
            according to self.formulas using the functions in tags. (course and formulas are set upon instantiation).
            If kwarg <writeDB> string is true, will write each function result to database table CourseStudentScore labed with
            appropriate tag.
            Will use all formulas by default, if no tags kwarg is specified.
        """
        context = {}
        scores = ExamScore.objects.values('exam__slug','score').filter(course=self.course, student=student)
        score_dict = collections.defaultdict(lambda:0)
        for s in scores:
            if s['score'] > score_dict[s['exam__slug']]:
                score_dict[s['exam__slug']] = s['score']

        #do reserved names
        score_dict = self.fill_reserved_word_context(score_dict, student_name=student.username)

        if tags is None:
            tags = self.formulas.keys()

        for tag in tags:
            if tag not in self.formulas:
                logger.warning("Tag %s was not found in the Aggregator's set of functions" % tag)
                continue
            
            #score_dict can now be used as a Context to populate formula as an arithmetic expression
            #without any variables
            formula = self.fill_formula(tag, score_dict)
            #print("%s: %s" % (tag, formula))
            
            #now we can do our restricted eval of our arithmetic expression
            ag_score = self.eval_helper(formula)
            #print("(%s,%s,%1.2f)" % (student.username, tag, ag_score))
            #now write to the DB if writeDB
            if writeDB:
                data, created = CourseStudentScore.objects.get_or_create(course=self.course, student=student, tag=tag)
                data.score = ag_score
                data.save()
                
        return ag_score

    def aggregate_all(self, tags=None, writeDB=False):
        """
            Does grade aggregation for all students in the course, using formulas specified in tags.
            If kwarg writeDB is specified, will write each formula result to database table CourseStudentScore labeled with appropriate
            tag.
            Will use all formulas by default, if no tags kwarg is specified.
        """
        students = self.course.get_all_students()
        processed = 0 
        for student in students:
            self.aggregate(student, tags=tags, writeDB=writeDB)
            processed += 1
        
            if processed % 100 == 0:
                print(processed)
                
    def eval_helper(self, formula):
        """ This helper function does a safe eval with restricted local environment and also wraps a bunch of
            try...excepts to catch and re-raise appropriate errors
        """
        try:
            return eval(formula, {"__builtins__":None}, self.safe_dict)
        except SyntaxError as e:
            raise AggregatorFormulaError("Your scoring formula has an syntax error in\n filename: %s line: %d offset: %d\n%s" \
                                 % (e.filename, e.lineno, e.offset, e.text))
        except Exception as e:
            raise AggregatorFormulaError(unicode(e))

    #########################################################################################################
    ###                                                                                                   ###
    ### BELOW HERE:  A selection of classmethods that auto-generate commonly-used formulas over a course. ###
    ###                                                                                                   ###
    #########################################################################################################

    @classmethod
    def generate_default_quiz_formula(selfclass, course):
        """ 
            This method will return a default quiz grading formula for the course, WHICH MUST BE READY MODE.
            The default logic is: 
                * linear sum of ExamScores, except
                    * take the max of all quizzes in the same Content Group
                    * In-Video Quizzes don't count
        """
        quizzes = set(Exam.objects.filter(course=course, exam_type='problemset', invideo=False, is_deleted=False, live_datetime__isnull=False))
        content_groups = ContentGroup.objects.filter(course=course, level=1, exam__isnull=False,
                                                     exam__exam_type='problemset', exam__live_datetime__isnull=False) \
                                             .select_related('exam').order_by("exam__live_datetime") #top level quizzes
        parent_quizzes = map(lambda g:g.exam, content_groups)

        all_quiz_groups = []
        #add all the quizzes that are in groups first
        for parent in parent_quizzes:
            groupinfo = ContentGroup.groupinfo_by_id('exam', parent.id)
            members = groupinfo['exam']
            slugs = map(lambda i: i.slug, members)
            all_quiz_groups.append(slugs)
            quizzes = quizzes-set(members)

        #print(quizzes)
        #now add quizzes that are singletons
        for q in quizzes:
            all_quiz_groups.append([q.slug])

        #print((all_quiz_groups))
        #now just output a formula that's a linear sum of the maxes of all the groups
        def stringify_inner_list(lst):
            return "max( %s )" % " , ".join(map(lambda li: "{{%s}}" % li, lst))

        strout = " + ".join(map(lambda li: stringify_inner_list(li), all_quiz_groups))
        #print(strout)
        return strout

    @classmethod
    def generate_default_exam_formula(selfclass, course):
        """
            This method will return a default exam grading formula for the course, WHICH MUST BE READY MODE.
            The default logic is:
            * linear sum of ExamScores, no consideration of groupings
        """
        exams = list(Exam.objects.values_list("slug", flat=True).filter(course=course,
                        exam_type='exam', invideo=False, is_deleted=False, live_datetime__isnull=False))

        strout = " + ".join(map(lambda slug: "{{%s}}" % slug, exams))
        #print(strout)
        return strout

    @classmethod
    def generate_default_exercise_formula(selfclass, course):
        """
            This method will return a default exam grading formula for the course, WHICH MUST BE READY MODE.
            The default logic is:
            * linear sum of ExamScores, no consideration of groupings
        """
        exercises = list(Exam.objects.values_list("slug", flat=True).filter(course=course,
                                                                            exam_type='interactive_exercise', invideo=False,
                                                                            is_deleted=False, live_datetime__isnull=False))
        
        strout = " + ".join(map(lambda slug: "{{%s}}" % slug, exercises))
        #print(strout)
        return strout

    @classmethod
    def generate_core_db_exercise_formula(selfclass, course):
        """
            This method will return a default exam grading formula for the course, WHICH MUST BE READY MODE.
            The default logic is:
            * linear sum of ExamScores, no consideration of groupings
            """
        exercises = list(Exam.objects.values_list("slug", flat=True).filter(course=course,
                                                                            exam_type='interactive_exercise', invideo=False,
                                                                            is_deleted=False, live_datetime__isnull=False) \
                                                                    .exclude(Q(slug__icontains="challenge") | Q(slug__icontains="extrapractice")))
        
        strout = " + ".join(map(lambda slug: "{{%s}}" % slug, exercises))
        #print(strout)
        return strout

    @classmethod
    def generate_challenge_db_exercise_formula(selfclass, course):
        """
            This method will return a default exam grading formula for the course, WHICH MUST BE READY MODE.
            The default logic is:
            * linear sum of ExamScores, no consideration of groupings
            """
        exercises = list(Exam.objects.values_list("slug", flat=True).filter(course=course, slug__icontains="challenge",
                                                                            exam_type='interactive_exercise', invideo=False,
                                                                            is_deleted=False, live_datetime__isnull=False))
        
        strout = " + ".join(map(lambda slug: "{{%s}}" % slug, exercises))
        #print(strout)
        return strout

    @classmethod
    def generate_db_course_formula(selfclass, course):
        return "%s + 2 * ( %s ) + 3 * ( %s )" % (selfclass.generate_default_quiz_formula(course),
                                                 selfclass.generate_core_db_exercise_formula(course),
                                                 selfclass.generate_default_exam_formula(course))
                                                 

#########################################################################################################
###                                                                                                   ###
### BELOW HERE:  Error classes used by the aggregator.                                                ###
###                                                                                                   ###
#########################################################################################################


class AggregatorError(Exception):
    """ Base class for Aggregator errors"""
    pass

class AggregatorFormulaError(AggregatorError):
    """ Raised when the formula that instantiates the Aggregator has an error (syntax, blacklisted function, etc)"""
    pass

class AggregatorFormulaVariableError(AggregatorError):
    """ Raised when one of the variables in the formula cannot be de-referenced (i.e. is not an Exam slug in self.course)"""
    pass

