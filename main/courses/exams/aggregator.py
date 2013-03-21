from c2g.models import ExamRecord, Exam, ExamScore, ExamRecordScore, Course, CourseStudentData, ContentGroup
from django.db.models import Q

import math
import collections
import re



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
    
    
    safe_dict = {'math':math, 'abs':abs, 'divmod':divmod, 'len':len, 'max':max, 'min':min,
        'pow':pow, 'range':range, 'sum':sum, 'map':map, 'filter':filter, 'reduce':reduce, 'list':list}

    def __init__(self, course, formula):
        """
            This function instantiates the aggregator with a course <course> and string <formula>.
            <course> MUST be a READY-MODE course.
            <formula> is a string written in a domain-specific language built on
            django templating and python.  Basically, formula should be a python
            expression that evaluates to a number, with function names in python syntax
            e.g. max(), min(), math.floor().  A variable namespace corresponding to
            student grades on individual assessments is also provided via a django
            template language syntax.  For example, {{exam1}} refers to the student's
            ExamScore on the Exam with slug==exam1.  So an example formula would be
            'max({{exam1a}} ,{{exam1b}})*0.5 + {{exam2}}*0.5'
        """
        self.course = course
        self.formula_str = formula
        #get a list variables used in the formula, so we can look them up
        self.formula_vars_patterns = self.var_re.findall(self.formula_str)
        self.formula_vars = map(lambda li: li[2:-2].strip(), self.formula_vars_patterns) #yeah yeah, hardcoding.  django templates does it too
        
        #now we try out the formula_vars to make sure they're all Exam slugs in the course
        for var in self.formula_vars:
            try:
                Exam.objects.get(course=course, slug=var)
            except Exam.DoesNotExist:
                raise AggregatorFormulaVariableError("{{%s}} is not an assessment item in Course %s" % (var, course))
        
        #now try out the formula with all variables filled in a 0's, to see if we throw any errors
        #score_dict will become the template context
        #set entire context to return 0
        score_dict = collections.defaultdict(lambda:0)
       
        formula = self.fill_formula(score_dict)
        #if there's a problem, this eval will raise an exception that will get passed on (no try...except)
        self.eval_helper(formula)

    def __unicode__(self):
        return self.formula_str + "\nAggregator formula for " + unicode(self.course)
    
    def max_points(self):
        exams = Exam.objects.filter(course=self.course, is_deleted=False, slug__in=self.formula_vars)
        points_dict = collections.defaultdict(lambda:0)
        for exam in exams:
            points_dict[exam.slug] = exam.get_total_score()
        formula = self.fill_formula(points_dict)
        print(formula)
        return self.eval_helper(formula)

    def fill_formula(self, context):
        """Fill out the formula pattern with context dict"""
        formula = self.formula_str
        for var in self.formula_vars:
            patt = r'{{\s*%s\s*}}' % re.escape(var)
            formula = re.sub(patt, str(context[var]), formula)
        return formula
    
    def aggregate(self, student, tag=None):
        """
            This function aggregates the <student>'s scores on assessments in self.course
            according to self.formula. (course and formula are set upon instantiation).
            If kwarg <tag> string is specified, will write result to database table with tag.
        """
        context = {}
        scores = ExamScore.objects.values('exam__slug','score').filter(course=self.course, student=student)
        score_dict = collections.defaultdict(lambda:0)
        for s in scores:
            if s['score'] > score_dict[s['exam__slug']]:
                score_dict[s['exam__slug']] = s['score']
        
        #default value is still 0, but may be found to be something else
        #for (patt, var) in zip(self.formula_vars_patterns, self.formula_vars):
        #    context[patt] = score_dict[var]
    
        #score_dict can now be used as a Context to populate formula as an arithmetic expression
        #without any variables
        formula = self.fill_formula(score_dict)
        print(formula)
        
        #now we can do our restricted eval of our arithmetic expression
        ag_score = self.eval_helper(formula)
        print(ag_score)
        #now write to the DB if tag is a string
        if isinstance(tag, str):
            data, created = CourseStudentData.objects.get_or_create(course=self.course, student=student, tag=tag)
            data.data = str(ag_score)
            data.save()
                
        return ag_score

    def aggregate_all(self, tag=None):
        """
            Does grade aggregation for all students in the course.
            If kwarg <tag> string is specified, will write result to database table with tag.
            
        """
        students = self.course.get_all_students()
        processed = 0 
        for student in students:
            self.aggregate(student, tag=tag)
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
        print(strout)
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

        strout = "3.0 * ( %s )" % " + ".join(map(lambda slug: "{{%s}}" % slug, exams))
        print(strout)
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
        
        strout = "2.0 * ( %s )" % " + ".join(map(lambda slug: "{{%s}}" % slug, exercises))
        print(strout)
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
        
        strout = "2.0 * ( %s )" % " + ".join(map(lambda slug: "{{%s}}" % slug, exercises))
        print(strout)
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
        
        strout = "2.0 * ( %s )" % " + ".join(map(lambda slug: "{{%s}}" % slug, exercises))
        print(strout)
        return strout



class AggregatorError(Exception):
    """ Base class for Aggregator errors"""
    pass

class AggregatorFormulaError(AggregatorError):
    """ Raised when the formula that instantiates the Aggregator has an error (syntax, blacklisted function, etc)"""
    pass

class AggregatorFormulaVariableError(AggregatorError):
    """ Raised when one of the variables in the formula cannot be de-referenced (i.e. is not an Exam slug in self.course)"""
    pass
