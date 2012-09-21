from django.core.management.base import BaseCommand, CommandError, make_option
from c2g.models import *
from django.contrib.auth.models import User,Group
from datetime import datetime
from random import randrange, shuffle
from django.db import connection, transaction

class Command(BaseCommand):
    help = "Populates the db with test development data. \n This command is <not> available on ready for obvious reasons. \n Settings can be made in file db_test_data/management/commands/db_populate.py"
    
    option_list = BaseCommand.option_list + (
        make_option('--massive',
            action='store_true',
            dest='massive',
            default=False,
            help='Populate the DB with mass-scale data (Warning: Can take a very long time to create the data on slower machines)'),
        )
        
    def handle(self, *args, **options):
        delete_db_data()
        
        if ('massive' in options) and (options['massive']):
            # Don't create fewer than 4 profs, 4 tas, 4 readonly tas, and 40 students
            user_counts = {'num_professors':10, 'num_tas':10, 'num_readonly_tas':10, 'num_students':40}
            content_counts = {'num_massive_courses':1, 'num_sections_per_course':2, 'num_videos_per_section':5}
        else:
            user_counts = {'num_professors':4, 'num_tas':4, 'num_readonly_tas':4, 'num_students':40}
            content_counts = {'num_massive_courses':0, 'num_sections_per_course':2, 'num_videos_per_section':5}
            
        
        # Create users
        print "      Creating users \r"
        print "      ----------------- \r"
        users = create_users(user_counts)

        # Create institutions
        institutions = create_institutions()

        # Create courses
        create_courses(institutions, users, content_counts)
        
        print "      ----------------------------- \r"
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

    #reset auto-increment counters
    cursor = connection.cursor()

    # Data modifying operation - commit required
    cursor.execute('alter table c2g_videos auto_increment = 1')


def create_users(user_counts):

    # Create professor accounts
    professors = []
    for i in range(user_counts['num_professors']):
        professors.append(User.objects.create_user('professor_' + str(i)))
        professors[i].set_password('class2go')
        professors[i].first_name = "Tess"
        professors[i].last_name = "Teacher"
        professors[i].email = "professor_%d@stanford.edu" % i
        professors[i].is_staff = 1
        professors[i].save()
        
        if user_counts['num_professors'] > 500 and (i%500 == 0):
            print "      Creating users >> Creating professors >> (%d/%d)complete\r" % (i,user_counts['num_professors'])

    # Create TA accounts
    tas = []
    for i in range(user_counts['num_tas']):
        tas.append(User.objects.create_user('ta_' + str(i)))
        tas[i].set_password('class2go')
        tas[i].first_name = "Alan"
        tas[i].last_name = "Assistant"
        tas[i].email = "ta_%d@stanford.edu" % i
        tas[i].save()
        
        if user_counts['num_tas'] > 500 and (i%500 == 0):
            print "      Creating users >> Creating tas >> (%d/%d)complete\r" % (i,user_counts['num_tas'])

    # Create Readonly-TA accounts
    readonly_tas = []
    for i in range(user_counts['num_readonly_tas']):
        readonly_tas.append(User.objects.create_user('readonly_ta_' + str(i)))
        readonly_tas[i].set_password('class2go')
        readonly_tas[i].first_name = "Roger"
        readonly_tas[i].last_name = "Readonly"
        readonly_tas[i].email = "readonly_ta_%d@stanford.edu" % i
        readonly_tas[i].save()
        
        if user_counts['num_readonly_tas'] > 500 and (i%500 == 0):
            print "      Creating users >> Creating read-only tas >> (%d/%d)complete\r" % (i,user_counts['num_readonly_tas'])

    # Create student accounts
    students = []
    for i in range(user_counts['num_students']):
        students.append(User.objects.create_user('student_' + str(i)))
        students[i].set_password('class2go')
        students[i].first_name = "Sarah"
        students[i].last_name = "Student"
        students[i].email = "student_%d@stanford.edu" % i
        students[i].save()
        
        if user_counts['num_students'] > 500 and (i%500 == 0):
            print "      Creating users >> Creating students >> (%d/%d)complete\r" % (i,user_counts['num_students'])

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

def create_courses(institutions,users,content_counts):
        
    # NLP Course
    data = {
        'institution': institutions[0],
        'title': 'Natural Language Processing',
        'description': 'Natural language processing is the technology for dealing with our most ubiquitous product: human language, as it appears in emails, web pages, tweets, product descriptions, newspaper stories, social media, and scientific articles, in thousands of languages and varieties. In the past decade, successful natural language processing applications have become part of our everyday experience, from spelling and grammar correction in word processors to machine translation on the web, from email spam detection to automatic question answering, from detecting people\'s opinions about products or services to extracting appointments from your email. In this class, you\'ll learn the fundamental algorithms and mathematical models for human alanguage processing and how you can use them to solve practical problems in dealing with language data wherever you encounter it.',
        'term': 'Fall',
        'year': 2012,
        'calendar_start': datetime(2013, 7, 27),
        'calendar_end': datetime(2013, 8, 12),
        'contact': 'nlp@123.com',
        'list_publicly': 1,
        'handle':'networking--Fall2012',
        'members': users,
    }
    print "      Creating networking course\r"
    print "      ------------------- \r"
    create_course_nlp(data, {'professors':users['professors'][0:3],'tas':users['tas'][0:3],'readonly_tas':users['readonly_tas'][0:3],'students':users['students'][0:39]})

    data = {
            'institution': institutions[0],
            'title': 'Introductory Cryptography',
            'description': 'Cryptography is an indispensable tool for protecting information in computer systems. This course explains the inner workings of cryptographic primitives and how to correctly use them. Students will learn how to reason about the security of cryptographic constructions and how to apply this knowledge to real-world applications. The course begins with a detailed discussion of how two parties who have a shared secret key can communicate securely when a powerful adversary eavesdrops and tampers with traffic. We will examine many deployed protocols and analyze mistakes in existing systems. The second half of the course discusses public-key techniques that let two or more parties generate a shared secret key. We will cover the relevant number theory and discuss public-key encryption, digital signatures, and authentication protocols. Towards the end of the course we will cover more advanced topics such as zero-knowledge, distributed protocols such as secure auctions, and a number of privacy mechanisms. Throughout the course students will be exposed to many exciting open problems in the field.The course will include written homeworks and programming labs. The course is self-contained, however it will be helpful to have a basic understanding of discrete probability theory.',
            'term': 'Fall',
            'year': 2012,
            'calendar_start': datetime(2013, 7, 27),
            'calendar_end': datetime(2013, 8, 12),
            'contact': 'crypto@123.com',
            'list_publicly': 1,
            'handle':'crypto--Fall2012',
            'members': users,
    }
    print "      Creating crypto course\r"
    print "      ---------------------- \r"
    create_course_crypto(data, {'professors':users['professors'][0:3],'tas':users['tas'][0:3],'readonly_tas':users['readonly_tas'][0:3],'students':users['students'][0:39]})
    
    # Massive: Create num_massive_courses massive courses
    for i in range(content_counts['num_massive_courses']):
        print "      Creating massive course %d of %d \r" % (i,content_counts['num_massive_courses'])
        print "      ------------------------------------- \r"
        create_course_massive(i, users, institutions, content_counts)
        
def create_course_massive(index, users, institutions, content_counts):
    
    terms = ["Fall", "Winter", "Spring", "Summer"]
    term_index = 0
    term = terms[term_index]
    
    year = 2012
    
    if term == "Fall":
        start_date = datetime(year, 9, randrange(1,21))
        end_date = datetime(year, 12, randrange(15,31))
    elif term == "Winter":
        start_date = datetime(year, 1, randrange(1,21))
        end_date = datetime(year, 3, randrange(15,31))
    elif term == "Spring":
        start_date = datetime(year, 4, randrange(1,21))
        end_date = datetime(year, 6, randrange(1,10))
    elif term == "Summer":
        start_date = datetime(year, 6, randrange(21,30))
        end_date = datetime(year, 9, randrange(1,4))

    # Create the course instances
    print "      Creating massive course %d of %d >> Creating course instances \r" % (index,content_counts['num_massive_courses'])
    student_group = Group.objects.create(name="Student Group for massive course " + " %d" % index)
    instructor_group = Group.objects.create(name="Instructor Group for massive course " + " %d" % index)
    tas_group = Group.objects.create(name="TAS Group for massive course " + " %d" % index)
    readonly_tas_group = Group.objects.create(name="Readonly TAS Group for massive course " + " %d" % index)
    
    course = Course(
            institution = institutions[0],
            student_group = student_group,
            instructor_group = instructor_group,
            tas_group = tas_group,
            readonly_tas_group = readonly_tas_group,
            title = "Massive Course %d" % index,
            description = "Massive course %d description" % index,
            term = term,
            year = year,
            calendar_start = start_date,
            calendar_end = end_date,
            list_publicly = 1,
            mode='draft',
            handle = "course"+str(index) + "--" + term + str(year)
        )

    course.save()
    course.create_ready_instance()
    
    # Add random users to course
    print "      Creating massive course %d of %d >> Adding Users >> Professors \r" % (index,content_counts['num_massive_courses'])
    for i in range(len(users['professors'])):
        instructor_group.user_set.add(users['professors'][i])
    
    print "      Creating massive course %d of %d >> Adding Users >> TAs \r" % (index,content_counts['num_massive_courses'])
    for i in range(len(users['tas'])):
        tas_group.user_set.add(users['tas'][i])
    
    print "      Creating massive course %d of %d >> Adding Users >> Read-only TAs \r" % (index,content_counts['num_massive_courses'])
    for i in range(len(users['readonly_tas'])):
        readonly_tas_group.user_set.add(users['readonly_tas'][i])
    
    print "      Creating massive course %d of %d >> Adding Users >> Students \r" % (index,content_counts['num_massive_courses'])  
    num_students = len(users['students'])
    for i in range(num_students):
        student_group.user_set.add(users['students'][i])
        if num_students > 500 and i%500 == 0:
            print "      Creating massive course %d of %d >> Adding Users >> Students >> (%d/%d) complete \r" % (index,content_counts['num_massive_courses'],i,num_students)
    
    print "      Creating massive course %d of %d >>  Adding course info pages\r" % (index,content_counts['num_massive_courses'])
    # Create the overview page
    str_ = ""
    for i in range(1000):
        str_ += "Overview for massive course %d" % index
        
    op = AdditionalPage(
        course=course,
        menu_slug='course_info',
        title="Overview for massive course %d" % index,
        description=str_,
        slug='overview',
        index=0,
        mode='draft',
    )
    op.save()
    op.create_ready_instance()
    
    # Create between 5 and 15 other course info menu pages
    num_pages = randrange(5,15)
    for i in range(num_pages):
        str_ = ""
        for j in range(1000):
            str_ += "Page %d for massive course %d" % (i, index)
            
        p = AdditionalPage(
            course=course,
            menu_slug='course_info',
            title= "Page %d for massive course %d" % (i, index),
            description=str_,
            slug='course_%d_page_%d' % (index, i),
            index=i+1,
            mode='draft',
        )
        p.save()
        p.create_ready_instance()
        
    # Add 20 announcements
    print "      Creating massive course %d of %d >>  Adding announcements\r" % (index,content_counts['num_massive_courses'])
    for i in range(20):
        str_ = ""
        for j in range(100):
            str_ += "Announcement %d for Course %d" % (i, index)
        
        a = Announcement(
            owner = course.instructor_group.user_set.all()[0],
            title = "Announcement %d for Course %d" % (i, index),
            description = str_,
            course = course
        )
        a.save()
        a.create_ready_instance()
        
        
    # Add exercises
    print "      Creating massive course %d of %d >>  Adding exercises\r" % (index,content_counts['num_massive_courses'])
    exercise1 = Exercise(
        fileName = "P1_Levenshtein.html",
        handle = "course"+str(index) + "--" + term + str(year)
    )
    exercise1.save()
    
    exercise2 = Exercise(
        fileName = "P1_Porter.html",
        handle = "course"+str(index) + "--" + term + str(year)
    )
    exercise2.save()
    
    exercise3 = Exercise(
        fileName = "P1_Regexp.html",
        handle = "course"+str(index) + "--" + term + str(year)
    )
    exercise3.save()
    
    exercise4 = Exercise(
        fileName = "P1_Tokenize.html",
        handle = "course"+str(index) + "--" + term + str(year)
    )
    exercise4.save()
    
    exercises = [exercise1, exercise2, exercise3, exercise4]
    
    
    # Sections, each with 5 videos, 1 problem set, and 1 static page
    yt_ids = ['BJiVRIPVNxU','dBVlwb15SBM','zJSqHRuD2C4','WMC3AjgYf3A','xOfEYI61f3k','Gh63CeMzav8','LRq7om7vMEc']
    durations = [722, 686, 366, 866, 426, 355, 522]
    print "      Creating massive course %d of %d >>  Adding content sections\r" % (index,content_counts['num_massive_courses'])
    
    for i in range(content_counts['num_sections_per_course']):
        draft_section = ContentSection(course=course, title="Section %d in Course %d" % (i, index), index=i, mode='draft')
        draft_section.save()
        draft_section.create_ready_instance()
        
        # Create 5 videos
        yt_index = randrange(0,6)
        for j in range(5):
            print "      Creating massive course %d of %d >>  Adding content section %d of %d >> Adding Video %d of 5\r" % (index,content_counts['num_massive_courses'], i, content_counts['num_sections_per_course'], j)
            print "      Creating massive course %d of %d >>  Adding content section %d of %d >> Adding Video %d of 5 >> Creating video objects\r" % (index,content_counts['num_massive_courses'], i, content_counts['num_sections_per_course'], j)
            video = Video(
                course = course,
                section = draft_section,
                title = "Video " + str(j) + " in Section " + str(i) + " in Course " +  str(index),
                description = "Description for Video " + str(j) + " in Section " + str(i) + " in Course " +  str(index),
                type = "youtube",
                url = yt_ids[yt_index],
                duration = durations[yt_index],
                slug = "section_" + str(i) + "_video_" + str(j),
                mode = 'draft',
                handle = "course"+str(index) + "--" + term + str(year),
                index = j,
            )
            video.save()
            video.create_ready_instance()
            prod = video.image; prod.live_datetime = datetime.now(); prod.save();
            
            # Add Exercises to Videos
            print "      Creating massive course %d of %d >>  Adding content section %d of %d >> Adding Video %d of 5 >> Adding exercises to video\r" % (index,content_counts['num_massive_courses'], i, content_counts['num_sections_per_course'], j)
            v2es = []
            for exercise in exercises:
                v2e = VideoToExercise(video=video, exercise=exercise, video_time=randrange(10,durations[yt_index]-10), is_deleted=0, mode='draft')
                v2e.save()
                v2e = VideoToExercise(video=video.image, exercise=exercise, video_time=randrange(10,durations[yt_index]-10), is_deleted=0, mode='ready')
                v2e.save()
                v2es.append(v2e)
            
            # Create view progress and exercise attempts for 75% of the users
            stud_index = 0
            for student in course.student_group.user_set.all():
                if randrange(0,3) > 0:
                    view_activity = VideoActivity(student = student, video = video.image, course = course.image, start_seconds = randrange(0,durations[yt_index]))
                    view_activity.save()
                    
                    for k in range(len(v2es)):
                        if v2es[k].video_time < view_activity.start_seconds:
                            problem_activity = ProblemActivity(
                                student = student,
                                video_to_exercise = v2es[k]
                            )
                            problem_activity.save()
                            
                stud_index += 1
                if num_students > 500 and stud_index%500 == 0:
                    print "      Creating massive course %d of %d >>  Adding content section %d of %d >> Adding Video %d of 5 >> Adding student video activity (%d/%d)\r" % (index,content_counts['num_massive_courses'], i, content_counts['num_sections_per_course'], j, stud_index, num_students)
                            
        # Create 1 static page
        print "      Creating massive course %d of %d >>  Adding content section %d of %d >> Adding 1 static page\r" % (index,content_counts['num_massive_courses'], i, content_counts['num_sections_per_course'])
        str_ = ""
        for j in range(1000):
            str_ += "Page for section %d in massive course %d" % (i, index)
            
        p = AdditionalPage(
            course=course,
            section = draft_section,
            title= "Page for section %d in massive course %d" % (i, index),
            description=str_,
            slug='course_%d_section_%d_page' % (index, i),
            index=6,
            mode='draft',
        )
        p.save()
        p.create_ready_instance()
        prod = p.image; prod.live_datetime = datetime.now(); prod.save();
                    
        # Create 1 problem set
        print "      Creating massive course %d of %d >>  Adding content section %d of %d >> Adding 1 problem set\r" % (index,content_counts['num_massive_courses'], i, content_counts['num_sections_per_course'])
        ps = ProblemSet(
            course = course,
            section = draft_section,
            slug = "course_"+str(index)+"_section_"+str(i)+"_ps",
            title = "Problem set for section %d" % i,
            description = "PS Description",
            due_date = datetime(2012, 9,19),
            grace_period = datetime(2012, 9,19),
            partial_credit_deadline = datetime(2012, 9,19),
            assessment_type = 'formative',
            late_penalty = 30,
            submissions_permitted = 3,
            resubmission_penalty = 30,
            randomize = False,
        )
        ps.save()
        ps.create_ready_instance()
        prod = ps.image; prod.live_datetime = datetime.now(); prod.save();
        
        for k in range(len(exercises)):
            ps2e = ProblemSetToExercise(problemSet=ps, exercise=exercises[k], number=k, is_deleted=0, mode='draft')
            ps2e.save()
            ps2e = ProblemSetToExercise(problemSet=ps.image, exercise=exercises[k], number=k, is_deleted=0, mode='ready')
            ps2e.save()
            
            stud_index = 0
            for student in course.student_group.user_set.all():
                if randrange(0,3) > 0:
                    problem_activity = ProblemActivity(
                        student = student,
                        problemset_to_exercise = ps2e
                    )
                    problem_activity.save()
                    
                stud_index += 1
                if num_students > 500 and stud_index%500 == 0:
                    print "      Creating massive course %d of %d >>  Adding content section %d of %d >> Adding 1 problem set >> Exercise %d of 4 >> Student activity (%d/%d)\r" % (index,content_counts['num_massive_courses'], i, content_counts['num_sections_per_course'], k, stud_index, num_students)
            
        
        

def create_course_nlp(data, users):
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
            mode='draft',
            handle = data['handle'])

    course.save()
    course.create_ready_instance()

    # Create the overview page
    op = AdditionalPage(
        course=course,
        menu_slug='course_info',
        title='Overview',
        description='Natural language processing is the technology for dealing with our most ubiquitous product: human language, as it appears in emails, web pages, tweets, product descriptions, newspaper stories, social media, and scientific articles, in thousands of languages and varieties. In the past decade, successful natural language processing applications have become part of our everyday experience, from spelling and grammar correction in word processors to machine translation on the web, from email spam detection to automatic question answering, from detecting people\'s opinions about products or services to extracting appointments from your email. In this class, you\'ll learn the fundamental algorithms and mathematical models for human alanguage processing and how you can use them to solve practical problems in dealing with language data wherever you encounter it.',
        slug='overview',
        index=0,
        mode='draft',
    )
    op.save()
    op.create_ready_instance()

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
    titles = ['Introduction and Regular Expressions', 'Tokenizations and Minimum Edit Distance', 'N-Grams']
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
    data['path']='/networking/Fall2012/problemsets/P1/load_problem_set'
    data['due_date']='2012-07-20'
    data['partial_credit_deadline']='2012-09-27'
    data['grace_period']='2012-10-27'
    data['late_penalty']=1
    data['submissions_permitted']=0
    data['resubmission_penalty']=25
    data['assessment_type']='formative'
    
    pset1 = create_problem_set(data, users)

    data['course'] = course
    data['section'] = sections[1]
    data['index'] = 3
    data['slug']='P2'
    data['description'] = 'This problem set will test your knowledge of Joint Probability. Each question is worth one point and your final exam is worth 100 points so these questions are basically useless. But you have to do them because an incomplete assignment disallows you from passing the class. Have fun with this problem set!'
    data['title']='Problem Set 2: Joint Probability'
    data['path']='/networking/Fall2012/problemsets/P2/load_problem_set'
    data['due_date']='2012-07-27'
    data['partial_credit_deadline']='2012-08-03'
    data['grace_period']='2012-10-27'
    data['late_penalty']=1
    data['submissions_permitted']=0
    data['resubmission_penalty']=25
    data['assessment_type']='formative'

    # Removing second problem set
    # KELVIN TODO -- fix create_problem_set so it handles two problem sets referencing the same exercises
    # duplicate exercise entries screws other things up.
    #
    pset2 = create_problem_set(data, users)

    #Create exercises
    exercise1_1 = save_exercise(pset1, "xx_P1_Regexp.html", 1, 'networking--Fall2012', 'networking/Fall2012/exercises/xx_P1_Regexp.html')
    exercise1_2 = save_exercise(pset1, "xx_P1_Tokenize.html", 2, 'networking--Fall2012', 'networking/Fall2012/exercises/xx_P1_Tokenize.html')

    exercise2_1 = save_exercise(pset2, "xx_P2_Lexical1.html", 1, 'networking--Fall2012', 'networking/Fall2012/exercises/xx_P2_Lexical1.html')

    # Create news events
    titles = [
        'Assignment 1 solutions and grades released',
        'Assignment 2 now available',
        'New video available: Ngrams',
    ]
    for i in range(3):
        create_news_event(course,titles[i])

def create_c2g_team():
    for (username,email,first,last) in [('sefk_auto','sefklon@gmail.com','Sef','Kloninger'),
                                        ('jbau_auto','jbau@stanford.edu','Jason','Bau'),
                                        ('wescott_auto','wescott@cs.stanford.edu','Mike','Wescott'),
                                        ('dcadams_auto','dcadams@stanford.edu','David','Adams'),
                                        ('jinpa_auto','jmanning@cs.stanford.edu','Jane','Manning'),
                                        ('halawa_auto','halawa@stanford.edu','Sherif','Halawa'),]:
        user=User.objects.create_user(username)
        user.set_password('class2go')
        user.first_name = first
        user.last_name = last
        user.email = email
        user.save()


def create_course_crypto(data, users):
    create_c2g_team()
    user1=User.objects.get(username='sefk_auto');
    user2=User.objects.get(username='jbau_auto');
    user3=User.objects.get(username='wescott_auto');
    user4=User.objects.get(username='dcadams_auto');
    user5=User.objects.get(username='jinpa_auto');
    user6=User.objects.get(username='halawa_auto');

    # Create the user groups
    r = randrange(0,100000000)
    student_group = Group.objects.create(name="Student Group for class2go course " + data['handle'] + " %d" % r)
    instructor_group = Group.objects.create(name="Instructor Group for class2go course " + data['handle'] + " %d" % r)
    tas_group = Group.objects.create(name="TAS Group for class2go course " + data['handle'] + " %d" % r)
    readonly_tas_group = Group.objects.create(name="Readonly TAS Group for class2go course " + data['handle'] + " %d" % r)

    # Join users to their groups
    for professor in [user2]:
        instructor_group.user_set.add(professor)
    for ta in [user1, user3]:
        tas_group.user_set.add(ta)
    for readonly_ta in [user4]:
        readonly_tas_group.user_set.add(readonly_ta)
    for student in [user5, user6]:
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
            mode='draft',
            handle = data['handle'])

    course.save()
    course.create_ready_instance()

    # Create the overview page
    op = AdditionalPage(
        course=course,
        menu_slug='course_info',
        title='Overview',
        description='Cryptography is an indispensable tool for protecting information in computer systems. This course explains the inner workings of cryptographic primitives and how to correctly use them. Students will learn how to reason about the security of cryptographic constructions and how to apply this knowledge to real-world applications.',
        slug='overview',
        index=0,
        mode='draft',
    )
    op.save()
    op.create_ready_instance()

    # Create announcements
    titles = [
        'Welcome to Crypto 223!',
        'Crypto: Assignment 1 Still Not Out',
        'Crypto: There is no lecture room for this course',
        'Crypto: Yet another assignment.'
    ]
    descriptions = [
        'Crypto: Welcome to the Crypto course! Check out the links to announcements, news events, assignments and grades.',
        'Crypto: The first assignment has been posted.  Visit the assignments link to see the list of assignments and instructions for each assignment.  Be sure to check the additional pages for additional help. If you have any question email us at nlp@stanford.edu.',
        'Crypto: Because this Friday is Friday the 13th, we do not want to take any chances so class is cancelled. Post any questions on the discussion forum if you have any questions',
        'Crypto: We will be moving the lecture room to the medical school. Sorry for any inconviniences. For those of you without a bike, I am even more sorry. See you next lecture!',
    ]
    for i in range(4):
        create_announcement(course, titles[i], descriptions[i], i, users['professors'][0])

    # Create content sections
    titles = ['Crypto: Introduction and md5', 'Crypto: md5 collisions', 'Crypto: Why not to use md5 any more']
    sections = []
    for i in range(3):
        sections.append(create_content_section(course, titles[i], i))

    # Create videos
    dicts = [
        {'course':course, 'section':sections[0], 'title':'Crypto: Course Introduction','description':'Intro video by Professor Dan Jurafsky and Chris Manning','type':'youtube','url':'BJiVRIPVNxU', 'duration':772, 'slug':'intro', 'index':0},
        {'course':course, 'section':sections[0], 'title':'Crypto: Regular Expressions','description':'Video on Regular Expressions','type':'youtube','url':'dBVlwb15SBM', 'duration':686, 'slug':'regexp', 'index':1},
        {'course':course, 'section':sections[0], 'title':'Crypto: Regular Expressions in Practical NLP','description':'Video on Regular Expressions in Practical NLP','type':'youtube','url':'zJSqHRuD2C4', 'duration':366, 'slug':'regexp_in_practical_nlp', 'index':2},
        {'course':course, 'section':sections[1], 'title':'Crypto: Word Tokenization','description':'Video on Word Tokenization','type':'youtube','url':'WMC3AjgYf3A', 'duration':866, 'slug':'tokenization', 'index':0},
        {'course':course, 'section':sections[1], 'title':'Crypto: Defining Minimum Edit Distance','description':'Video on Defining Minimum Edit Distance','type':'youtube','url':'xOfEYI61f3k', 'duration':426, 'slug':'min_edit_distance', 'index':1},
        {'course':course, 'section':sections[1], 'title':'Crypto: Computing Minimum Edit Distance','description':'Video on Computing Minimum Edit Distance','type':'youtube','url':'Gh63CeMzav8', 'duration':355, 'slug':'computing_min_edit_distance', 'index':2},
        {'course':course, 'section':sections[2], 'title':'Crypto: Introduction to N-grams','description':'Video on Introduction to N-grams','type':'youtube','url':'LRq7om7vMEc', 'duration':522, 'slug':'ngrams', 'index':0},
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
    data['description'] = 'Crypto: This is the first problem set. Practice some question on Regular Expressions. Remember to work your problems out on a separate piece of paper first because you only get one try on these. Miss on and you have a D!'
    data['title'] = 'Crypto: Problem Set 1: Regular Expressions'
    data['path']='/static/latestKhan/exercises/P1.html'
    data['due_date']='2012-07-20'
    data['partial_credit_deadline']='2012-07-27'
    data['grace_period']='2013-07-27'
    data['late_penalty'] = 5
    data['submissions_permitted'] = 0
    data['resubmission_penalty'] = 10

  #  pset1 = create_problem_set(data, users)

    data['course'] = course
    data['section'] = sections[1]
    data['index'] = 3
    data['slug']='P2'
    data['description'] = 'Crypto: This problem set will test your knowledge of Joint Probability. Each question is worth one point and your final exam is worth 100 points so these questions are basically useless. But you have to do them because an incomplete assignment disallows you from passing the class. Have fun with this problem set!'
    data['title']='Crypto: Problem Set 2: Joint Probability'
    data['path']='/static/latestKhan/exercises/P2.html'
    data['due_date']='2012-07-27'
    data['partial_credit_deadline']='2012-08-03'

    # Removing second problem set
    # KELVIN TODO -- fix create_problem_set so it handles two problem sets referencing the same exercises
    # duplicate exercise entries screws other things up.
    #
    # pset2 = create_problem_set(data, users)

    #Create exercises

    #exercise1_1 = save_exercise(pset1, "xx_P1_Levenshtein_1Q.html", 1, 'crypto#$!Fall2012')
    
  #  url = 'http://localhost:8080/nlp/Fall2012/problemsets/P1/manage_exercise'
  #  payload = {'user': 'professor_1', 'password': 'class2go'}

  #  r = requests.post(url, data=payload)
  #  print '------' + str(r.text)
  #  print '++++++' + str(r.status_code)
    
    
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
        'Crypto: Assignment 1 solutions and grades released',
        'Crypto: Assignment 2 now available',
        'Crypto: New video available: Ngrams',
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
        mode = 'draft',
    )
    announcement.save()
    announcement.create_ready_instance()

def create_content_section(course, title, index):
    section = ContentSection(
        course=course,
        title=title,
        index=index,
        mode='draft',
    )
    section.save()
    section.create_ready_instance()
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
        mode='draft',
        handle=data['course'].handle,
    )
    video.save()
    video.create_ready_instance()

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
        grace_period = data['grace_period'],
        late_penalty = data['late_penalty'],
        submissions_permitted = data['submissions_permitted'],
        resubmission_penalty = data['resubmission_penalty'],
        description = data['description'],
        mode='draft',
        index=data['index'],
        assessment_type=data['assessment_type']
    )
    problem_set.save()
    prod_instance =  problem_set.create_ready_instance()

    problem_set.save()

    # @todo: Create exercises, problems, and user activity for problem sets based on the new draft/ready paradigm

    #Shouldn't need to populate exercises since they can be uploaded now
    #save_exercise(problem_set, "P1_Levenshtein.html", 1)
    #save_exercise(problem_set, "P1_Regexp.html", 2)
    #save_exercise(problem_set, "P1_Tokenize.html", 3)
    #save_exercise(prod_instance, "P1_Levenshtein.html", 1)
    #save_exercise(prod_instance, "P1_Regexp.html", 2)
    #save_exercise(prod_instance, "P1_Tokenize.html", 3)

    return problem_set


def save_exercise(problemSet, fileName, number, handle, file):
    ex = Exercise(fileName = fileName)
    ex.file = file
    ex.handle = handle
    ex.save()

    psetToEx = ProblemSetToExercise(problemSet = problemSet,
                                    exercise = ex,
                                    number = number)
    psetToEx.save()
    #psetToEx.create_ready_instance()

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
