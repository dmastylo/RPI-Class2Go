from django.core.management.base import BaseCommand, CommandError
from c2g.models import *
from django.contrib.auth.models import User,Group
from datetime import datetime
from random import randrange

class Command(BaseCommand):
    help = "Populates the db with test development data. \n This command is <not> available on production for obvious reasons. \n Settings can be made in file db_test_data/management/commands/db_populate.py"

    def handle(self, *args, **options):
        delete_db_data()

        # Create users
        users = create_users()

        # Create institutions
        institutions = create_institutions()

        # Create courses
        create_courses(institutions, users)

        print "      Successfully populated the db \r"


def delete_db_data():

    #Since all tables are foreign key related, this deletes all data in all c2g tables
    Institution.objects.all().delete()

    # Nuke the data that we create below.  Order doesn't seem to matter.
    Course.objects.all().delete()
    AdditionalPage.objects.all().delete()
    Announcement.objects.all().delete()
    ContentSection.objects.all().delete()
    ProblemSet.objects.all().delete()
    Video.objects.all().delete()
    ProblemSetToExercise.objects.all().delete()
    Exercise.objects.all().delete()
    ProblemActivity.objects.all().delete()
    NewsEvent.objects.all().delete()

    Group.objects.all().delete()
    User.objects.all().delete()

def create_users():
    # Create professor accounts
    professors = []
    for i in range(3):
        professors.append(User.objects.create_user('professor_' + str(i)))
        professors[i].set_password('class2go')
        professors[i].is_staff = 1
        professors[i].save()

    # Create TA accounts
    tas = []
    for i in range(3):
        tas.append(User.objects.create_user('ta_' + str(i)))
        tas[i].set_password('class2go')
        tas[i].save()

    # Create Readonly-TA accounts
    readonly_tas = []
    for i in range(3):
        readonly_tas.append(User.objects.create_user('readonly_ta_' + str(i)))
        readonly_tas[i].set_password('class2go')
        readonly_tas[i].save()

    # Create student accounts
    students = []
    for i in range(40):
        students.append(User.objects.create_user('student_' + str(i)))
        students[i].set_password('class2go')
        students[i].save()

    return {'professors':professors, 'tas':tas, 'readonly_tas':readonly_tas, 'students':students}


def create_institutions():
    institutions = []
    for n in range(1):
        title = "Institution_" + str(n)
        country = 'USA'
        city = 'Palo Alto'
        domains = 'stanford.edu'

        institution =Institution(
            title = title,
            country = country,
            city = city,
            domains = domains
        )
        institution.save()

        institutions.append(institution)

    return institutions

def create_courses(institutions,users):
    # Currently, only create the NLP course
    data = {
        'institution': institutions[0],
        'title': 'Natural Language Processing',
        'description': 'Natural language processing is the technology for dealing with our most ubiquitous product: human language, as it appears in emails, web pages, tweets, product descriptions, newspaper stories, social media, and scientific articles, in thousands of languages and varieties. In the past decade, successful natural language processing applications have become part of our everyday experience, from spelling and grammar correction in word processors to machine translation on the web, from email spam detection to automatic question answering, from detecting people\'s opinions about products or services to extracting appointments from your email. In this class, you\'ll learn the fundamental algorithms and mathematical models for human alanguage processing and how you can use them to solve practical problems in dealing with language data wherever you encounter it.',
        'term': 'Fall',
        'year': 2012,
        'calendar_start': datetime(2012, 7, 27),
        'calendar_end': datetime(2012, 8, 12),
        'list_publicly': 1,
        'handle':'nlp#$!Fall2012',
        'members': users,
    }
    create_course(data, users)

def create_course(data, users):
    # Create the user groups
    r = randrange(0,100000000)
    student_group = Group.objects.create(name="Student Group for class2go course " + data['handle'] + " %d" % r)
    instructor_group = Group.objects.create(name="Instructor Group for class2go course " + data['handle'] + " %d" % r)
    tas_group = Group.objects.create(name="TAS Group for class2go course " + data['handle'] + " %d" % r)
    readonly_tas_group = Group.objects.create(name="Readonly TAS Group for class2go course " + data['handle'] + " %d" % r)

    # Join users to their groups
    for professor in users['professors']:
        instructor_group.user_set.add(professor)
    for ta in users['tas']:
        tas_group.user_set.add(ta)
    for readonly_ta in users['readonly_tas']:
        readonly_tas_group.user_set.add(readonly_ta)
    for student in users['students']:
        student_group.user_set.add(student)

    # Create the course instances
    course = Course(institution = data['institution'],
            student_group = student_group,
            instructor_group = instructor_group,
            tas_group = tas_group,
            readonly_tas_group = readonly_tas_group,
            title = data['title'],
            description = data['description'],
            term = data['term'],
            year = data['year'],
            calendar_start = data['calendar_start'],
            calendar_end = data['calendar_end'],
            list_publicly = data['list_publicly'],
            mode='staging',
            handle = data['handle'])

    course.save()
    course.create_production_instance()

    # Create the overview page
    op = AdditionalPage(
        course=course,
        menu_slug='course_info',
        title='Overview',
        description='Natural language processing is the technology for dealing with our most ubiquitous product: human language, as it appears in emails, web pages, tweets, product descriptions, newspaper stories, social media, and scientific articles, in thousands of languages and varieties. In the past decade, successful natural language processing applications have become part of our everyday experience, from spelling and grammar correction in word processors to machine translation on the web, from email spam detection to automatic question answering, from detecting people\'s opinions about products or services to extracting appointments from your email. In this class, you\'ll learn the fundamental algorithms and mathematical models for human alanguage processing and how you can use them to solve practical problems in dealing with language data wherever you encounter it.',
        slug='overview',
        index=0,
        mode='staging',
    )
    op.save()
    op.create_production_instance()

    # Create announcements
    titles = [
        'Welcome to Natural Language Processing!',
        'Assignment 1 Out',
        'Friday Lecture for 7/13 cancelled',
        'Lecture Room Moved'
    ]
    descriptions = [
        'Welcome to the course! Check out the links to announcements, news events, assignments and grades.',
        'The first assignment has been posted.  Visit the assignments link to see the list of assignments and instructions for each assignment.  Be sure to check the additional pages for additional help. If you have any question email us at nlp@stanford.edu.',
        'Because this Friday is Friday the 13th, we do not want to take any chances so class is cancelled. Post any questions on the discussion forum if you have any questions',
        'We will be moving the lecture room to the medical school. Sorry for any inconviniences. For those of you without a bike, I am even more sorry. See you next lecture!',
    ]
    for i in range(4):
        create_announcement(course, titles[i], descriptions[i], i, users['professors'][0])

    # Create content sections
    titles = ['NLP Introduction and Regular Expressions', 'Tokenizations and Minimum Edit Distance', 'N-Grams']
    sections = []
    for i in range(3):
        sections.append(create_content_section(course, titles[i], i))

    # Create videos
    dicts = [
        {'course':course, 'section':sections[0], 'title':'Course Introduction','description':'Intro video by Professor Dan Jurafsky and Chris Manning','type':'youtube','url':'BJiVRIPVNxU', 'duration':772, 'slug':'intro', 'index':0},
        {'course':course, 'section':sections[0], 'title':'Regular Expressions','description':'Video on Regular Expressions','type':'youtube','url':'dBVlwb15SBM', 'duration':686, 'slug':'regexp', 'index':1},
        {'course':course, 'section':sections[0], 'title':'Regular Expressions in Practical NLP','description':'Video on Regular Expressions in Practical NLP','type':'youtube','url':'zJSqHRuD2C4', 'duration':366, 'slug':'regexp_in_practical_nlp', 'index':2},
        {'course':course, 'section':sections[1], 'title':'Word Tokenization','description':'Video on Word Tokenization','type':'youtube','url':'WMC3AjgYf3A', 'duration':866, 'slug':'tokenization', 'index':0},
        {'course':course, 'section':sections[1], 'title':'Defining Minimum Edit Distance','description':'Video on Defining Minimum Edit Distance','type':'youtube','url':'xOfEYI61f3k', 'duration':426, 'slug':'min_edit_distance', 'index':1},
        {'course':course, 'section':sections[1], 'title':'Computing Minimum Edit Distance','description':'Video on Computing Minimum Edit Distance','type':'youtube','url':'Gh63CeMzav8', 'duration':355, 'slug':'computing_min_edit_distance', 'index':2},
        {'course':course, 'section':sections[2], 'title':'Introduction to N-grams','description':'Video on Introduction to N-grams','type':'youtube','url':'LRq7om7vMEc', 'duration':522, 'slug':'ngrams', 'index':0},
    ]

    for i in range(7):
        create_video(dicts[i], users)

    # Create problem sets
    #Kelvin - Stopping the creation of problem sets because there's no easy way to add a file and you
    #can already use the gui to add problem sets and pick your own exercises.
    data['course'] = course
    data['section'] = sections[0]
    data['index'] = 3
    data['slug']='P1'
    data['description'] = 'This is the first problem set. Practice some question on Regular Expressions. Remember to work your problems out on a separate piece of paper first because you only get one try on these. Miss on and you have a D!'
    data['title'] = 'Problem Set 1: Regular Expressions'
    data['path']='/static/latestKhan/exercises/P1.html'
    data['due_date']='2012-07-20'
    data['partial_credit_deadline']='2012-07-27'

    #pset1 = create_problem_set(data, users)

    data['course'] = course
    data['section'] = sections[1]
    data['index'] = 3
    data['slug']='P2'
    data['description'] = 'This problem set will test your knowledge of Joint Probability. Each question is worth one point and your final exam is worth 100 points so these questions are basically useless. But you have to do them because an incomplete assignment disallows you from passing the class. Have fun with this problem set!'
    data['title']='Problem Set 2: Joint Probability'
    data['path']='/static/latestKhan/exercises/P2.html'
    data['due_date']='2012-07-27'
    data['partial_credit_deadline']='2012-08-03'

    # Removing second problem set
    # KELVIN TODO -- fix create_problem_set so it handles two problem sets referencing the same exercises
    # duplicate exercise entries screws other things up.
    #
    # pset2 = create_problem_set(data, users)

    #Create exercises

#    exercise1_1 = save_exercise(pset1, "P1_Levenshtein.html", 1)
#    exercise1_2 = save_exercise(pset1, "P1_Regexp.html", 2)
#    exercise1_3 = save_exercise(pset1, "P1_Tokenize.html", 3)

#    exercise2_1 = save_exercise(pset2, "P2_Add_one_smoothing.html", 1)
#    exercise2_2 = save_exercise(pset2, "P2_Joint.html", 2)
#    exercise2_3 = save_exercise(pset2, "P2_Lexical1.html", 3)
#    exercise2_4 = save_exercise(pset2, "P2_NER1.html", 4)
#    exercise2_5 = save_exercise(pset2, "P2_Spelling.html", 5)

    #Create problems

    # save_problem(exercise1_1, 'p1')
    # save_problem(exercise1_1, 'p2')
    # save_problem(exercise1_2, 'p1')
    # save_problem(exercise1_3, 'p1')

    # save_problem(exercise2_1, 'p1')
    # save_problem(exercise2_1, 'p2')
    # save_problem(exercise2_2, 'p1')
    # save_problem(exercise2_3, 'p1')
    # save_problem(exercise2_4, 'p1')
    # save_problem(exercise2_5, 'p1')

    # Create news events
    titles = [
        'Assignment 1 solutions and grades released',
        'Assignment 2 now available',
        'New video available: Ngrams',
    ]
    for i in range(3):
        create_news_event(course,titles[i])



def create_announcement(course, title, description, index, owner):
    announcement = Announcement(
        course=course,
        title = title,
        description = description,
        index = index,
        owner = owner,
        mode = 'staging',
    )
    announcement.save()
    announcement.create_production_instance()

def create_content_section(course, title, index):
    section = ContentSection(
        course=course,
        title=title,
        index=index,
        mode='staging',
    )
    section.save()
    section.create_production_instance()
    return section

def create_video(data, users):
    # Also creates random progress for each user for each video
    video = Video(
        course=data['course'],
        section=data['section'],
        title=data['title'],
        description=data['description'],
        type=data['type'],
        url=data['url'],
        duration=data['duration'],
        slug=data['slug'],
        file="default",
        index=data['index'],
        mode='staging',
        handle=data['course'].handle,
    )
    video.save()
    video.create_production_instance()

    for user in users['students']:
        video_activity = VideoActivity(
            student=user,
            course=data['course'],
            video=video.image,
            start_seconds = randrange(0,int(video.duration))
        )
        video_activity.save()

def create_news_event(course,title):
    event = NewsEvent(
        course=course.image,
        event=title,
    )
    event.save()
    return event


def create_problem_set(data, users):
    problem_set = ProblemSet(
        course = data['course'],
        section = data['section'],
        slug = data['slug'],
        title = data['title'],
        path = data['path'],
        due_date = data['due_date'],
        partial_credit_deadline = data['partial_credit_deadline'],
        description = data['description'],
        mode='staging',
        index=data['index'],
    )
    problem_set.save()
    prod_instance =  problem_set.create_production_instance()

    problem_set.save()

    # @todo: Create exercises, problems, and user activity for problem sets based on the new staging/production paradigm

    #Shouldn't need to populate exercises since they can be uploaded now
    #save_exercise(problem_set, "P1_Levenshtein.html", 1)
    #save_exercise(problem_set, "P1_Regexp.html", 2)
    #save_exercise(problem_set, "P1_Tokenize.html", 3)
    #save_exercise(prod_instance, "P1_Levenshtein.html", 1)
    #save_exercise(prod_instance, "P1_Regexp.html", 2)
    #save_exercise(prod_instance, "P1_Tokenize.html", 3)

    return problem_set


def save_exercise(problemSet, fileName, number):
    ex = Exercise(fileName = fileName)
    ex.save()
    psetToEx = ProblemSetToExercise(problemSet = problemSet,
                                    exercise = ex,
                                    number = number)
    psetToEx.save()
    return ex

def save_problem(exercise, slug):
    problem = Problem(exercise = exercise,
                    slug = slug)

    problem.save()

# def save_problem_activity(student, problem):
    # problem_activity = ProblemActivity(student = student,
                                        # course_id = course_id,
                                        # problem = problem,
                                        # problem_set = problem_set)
    # problem_activity.save()
