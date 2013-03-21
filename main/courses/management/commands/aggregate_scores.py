from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from c2g.models import Course
from django.contrib.auth.models import User
from courses.exams.aggregator import ScoreAggregator

class Command(BaseCommand):
    args = "<course_id> <formula_file>"
    help = "Aggregates assessment scores (ExamScore) for course <course_id> according\nto the formula specified in <formula_file>.\nBy default a dry-run unless -t or --tag is specified."

    option_list = (
        make_option("-t", "--tag", dest="tag", default=None,
            help="If tag is specified, will put formula result into CourseStudentData table as (course, student, tag) => result"),
    ) + BaseCommand.option_list

    def handle(self, *args, **options): 
        if len(args) != 2:
           raise CommandError("Wrong number of arguments.  Should be exactly 2: <course_id> <formula_file>")
        
        try:
            course = Course.objects.get(id=args[0])
            print ("Aggregating grades for %s" % unicode(course))
        except Course.DoesNotExist:
            raise CommandError("The specified course_id %s does not exist." % args[0])

        file = open(args[1]) #just let any exceptions here propagate
        formula_str = file.read()
        file.close()
    
        tag = options['tag']
        if not isinstance(tag, str):
            print("dryrun")
        else:
            print("storing results in CourseStudentData table under tag " + tag)
    
        #agg = ScoreAggregator(course, formula_str)
        #print(unicode(agg))

        agg=ScoreAggregator(course, " + ".join([ScoreAggregator.generate_default_quiz_formula(course),
                                                ScoreAggregator.generate_default_exam_formula(course),
                                                ScoreAggregator.generate_challenge_db_exercise_formula(course),
                                                ScoreAggregator.generate_core_db_exercise_formula(course)]))
        admin = User.objects.get(username='admin')
        agg.aggregate(admin, tag=tag)
