from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from c2g.models import Course
from django.contrib.auth.models import User
from courses.exams.aggregator import ScoreAggregator

class Command(BaseCommand):
    args = "<course_handle>"
    help = "Aggregates assessment scores (ExamScore) for course <course_handle> according to the default course formulas.\nBy default a dry-run unless you use the -u or --update options."

    option_list = (
        make_option("-t", "--tag", dest="tag",
            help="If tag is specified, will aggregate using formula loaded from <file> with tag <tag>.  Must be used in conjuction with -f"),
        make_option("-f", "--file", dest="file",
            help="If file is specified, will aggregate using formula loaded from <file> with tag <tag>.  Must be used in conjuction with -t"),
        make_option("-u", "--update", dest="update", action="store_true",
            help="If update is specified, will write to CourseStudentScore table after the result of aggregation calculations.  The default tags (or the one specified with -t) will be used for the tag column."),
        make_option("-s", "--student", dest="username", default="",
            help="If <student> is specified, only aggregate for student with username=<student>, rather than the entire student roster."),
    ) + BaseCommand.option_list

    def handle(self, *args, **options): 
        if len(args) != 1:
           raise CommandError("Wrong number of arguments.  Should be exactly 1: <course_handle>")
        
        
        try:
            course = Course.objects.get(handle=args[0], mode="ready")
            print ("Aggregating grades for %s" % unicode(course))
        except Course.DoesNotExist:
            raise CommandError("The specified course_id %s does not exist." % args[0])

        if options['file'] is not None and options['tag'] is None or \
           options['file'] is None and options['tag'] is not None:
            raise CommandError("You must use -t and -f together")
    
        student = None
        if options['username']:
            try:
                student = User.objects.get(username=options['username'])
            except User.DoesNotExist:
                raise CommandError("No user with username %s" % options['username'])

        if options['file']:
            file = open(options['file']) #just let any exceptions here propagate
            formula_str = file.read()
            file.close()
            tag = options['tag']
            print("Creating aggregator %s" % tag)
            agg = ScoreAggregator(course, formulas={tag: formula_str})
            print(unicode(agg))
        else:
            quiz_formula = ScoreAggregator.generate_default_quiz_formula(course)
            exam_formula = ScoreAggregator.generate_default_exam_formula(course)
            core_ex_formula = ScoreAggregator.generate_core_db_exercise_formula(course)
            challenge_ex_formula = ScoreAggregator.generate_challenge_db_exercise_formula(course)
            db_formula = ScoreAggregator.generate_db_course_formula(course)
            agg=ScoreAggregator(course, formulas=\
                                {'quizzes' : quiz_formula,
                                 'exams'   : exam_formula,
                                 'core-exercises' : core_ex_formula,
                                 'accomplishment' : db_formula,
                                 'challenge-exercises': challenge_ex_formula})
            print(unicode(agg))

        if student:
            agg.aggregate(student, writeDB=options['update'])
        else:
            agg.aggregate_all(writeDB=options['update'])
