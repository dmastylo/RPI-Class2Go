from c2g.models import *
from django.contrib.auth.models import User,Group


def delete_db_data():

    #Since all tables are foreign key related, this deletes all data in all c2g tables
    Institution.objects.all().delete()

    # Nuke the data that we create below.  Order doesn't seem to matter.
    Course.objects.all().delete()
    Announcement.objects.all().delete()
    NewsEvent.objects.all().delete()

    Group.objects.all().delete()
    User.objects.all().delete()

def create_institutions(create_course_data, create_user_data):

    for n in range(0,10):
        title = "Institution_" + str(n)
        country = 'USA'
        city = 'Palo Alto'
        domains = 'stanford.edu'

        institution = Institution(title = title,
                                  country = country,
                                  city = city,
                                  domains = domains)

        institution.save()

        if create_course_data == 1:
            for p in range(0,10):

                institution_id = institution.id
                code = 'CS101_' + str(p)
                title = 'Introduction to Computers' + str(p)
                listing_description = 'CS107 is the third course in Stanford\'s introductory programming sequence. \n Our CS106 courses provide students with a solid foundation in programming methodology and abstractions and CS107 follows on to build up their programming maturity and expand breadth and depth of experience. \n\n The course will work from the C programming language down to the microprocessor to de-mystify the machine. With a complete understanding of how computer systems execute programs and manipulate data, you will become a more effective programmer, especially in dealing with issues of debugging, performance, portability, and robustness. Topics covered include: the C programming language, data representation, machine-level code, computer arithmetic, elements of code compilation, performance evaluation and optimization, and memory organization and management.The class has three lectures a week and a weekly lab designed for hands-on learning and experimentation. There will be significant programming assignments and you can expect to work hard and be challenged by this course. Your effort can really pay off - once you master the machine and advance your programming skills to the next level, you will have powerful mojo to bring to any future project!'
                mode = 'live'
                description = 'CS107 is the third course in Stanford\'s introductory programming sequence.'
                staff_emails = 'aa.123.edu,bb.123.edu'
                term = 'Winter'
                year = '2012'
                calendar_start = '2012-07-24'
                calendar_end = '2012-09-24'
                meeting_info = 'There are no upcoming office hours'
                feature_settings = 'assignments=on,lectures=off'
                membership_control = '1,2,3'
                list_publicly = '0'
                handle = str(code) + str(term) + str(year) + str(institution_id)

                course = Course(institution_id = institution_id,
                                code = code,
                                title = title,
                                listing_description = listing_description,
                                mode = mode,
                                description = description,
                                staff_emails = staff_emails,
                                term = term,
                                year = year,
                                calendar_start = calendar_start,
                                calendar_end = calendar_end,
                                meeting_info = meeting_info,
                                feature_settings = feature_settings,
                                membership_control = membership_control,
                                list_publicly = list_publicly,
                                handle = handle)

                course.save()

                if create_user_data == 1:
                    for q in range(0,10):

                        #Create the user
                        user = User.objects.create_user('test_' + str(course.id) + '_' + str(q))
                        course.student_group.user_set.add(user)


def create_nlp_course():
    
        #Create the Institution
        title = "Stanford University"
        country = 'USA'
        city = 'Palo Alto'
        domains = 'stanford.edu'

        institution = Institution(title = title,
                                  country = country,
                                  city = city,
                                  domains = domains)

        institution.save()
        
        #Create the course
        institution_id = institution.id
        code = 'CS1234'
        title = 'Natural Language Processing'
        listing_description = 'This course covers a broad range of topics in natural language processing, including word and sentence tokenization, text classification and sentiment analysis, spelling correction, information extraction, parsing, meaning extraction, and question answering, We will also introduce the underlying theory from probability, statistics, and machine learning that are crucial for the field, and cover fundamental algorithms like n-gram language modeling, naive bayes and maxent classifiers, sequence models like Hidden Markov Models, probabilistic dependency and constituent parsing, and vector-space models of meaning.We are offering this course on Natural Language Processing free and online to students worldwide, continuing Stanford\'s exciting forays into large scale online instruction. Students have access to screencast lecture videos, are given quiz questions, assignments and exams, receive regular feedback on progress, and can participate in a discussion forum. Those who successfully complete the course will receive a statement of accomplishment. Taught by Professors Jurafsky and Manning, the curriculum draws from Stanford\'s courses in Natural Language Processing. You will need a decent internet connection for accessing course materials, but should be able to watch the videos on your smartphone.'
        mode = 'live'
        description = 'Natural language processing is the technology for dealing with our most ubiquitous product: human language, as it appears in emails, web pages, tweets, product descriptions, newspaper stories, social media, and scientific articles, in thousands of languages and varieties. In the past decade, successful natural language processing applications have become part of our everyday experience, from spelling and grammar correction in word processors to machine translation on the web, from email spam detection to automatic question answering, from detecting people\'s opinions about products or services to extracting appointments from your email. In this class, you\'ll learn the fundamental algorithms and mathematical models for human language processing and how you can use them to solve practical problems in dealing with language data wherever you encounter it.'
        staff_emails = 'aa@stanford.edu*, bb@stanford.edu*'
        term = 'Fall'
        year = '2012'
        calendar_start = '2012-07-24'
        calendar_end = '2012-09-24'
        meeting_info = 'There are no upcoming office hours'
        feature_settings = 'assignments=on,lectures=on,videos=on'
        membership_control = '1,2,3'
        list_publicly = '1'
        handle = 'nlp-Fall2012'
        
        #Create the Course
        course = Course(institution_id = institution_id,
                        code = code,
                        title = title,
                        listing_description = listing_description,
                        mode = mode,
                        description = description,
                        staff_emails = staff_emails,
                        term = term,
                        year = year,
                        calendar_start = calendar_start,
                        calendar_end = calendar_end,
                        meeting_info = meeting_info,
                        feature_settings = feature_settings,
                        membership_control = membership_control,
                        list_publicly = list_publicly,
                        handle = handle)

        course.save()

        #Create the Video Topics
        course_id = course.id
        title = 'Section 1 Download'
        save_video_topic (course_id, title)
        
        title = '1.1 Course Intro'
        save_video_topic (course_id, title)
        
        title = '1.2 History of Field'
        save_video_topic (course_id, title)
        
        title = '1.3 Big Issues'
        save_video_topic (course_id, title)
        
        #Create Additional Pages
        course_id = course_id
        access_id = '123'
        write_access = '1,2'
        
        
        title = 'Syllabus'
        description = 'description of Syllabus'
        save_additional_page(course_id, access_id, write_access, title, description)
        
        title = 'Other Static Page 1'
        description = 'description of other static page 1'
        save_additional_page(course_id, access_id, write_access, title, description)
        
        title = 'Other Static Page 2'
        description = 'description of other static page 2'
        save_additional_page(course_id, access_id, write_access, title, description)        
        
        
        #Create some Student Users
        for q in range(0,10):

            user = User.objects.create_user('nlp_student_' + str(q))
            user.set_password('class2go')
            user.save()
            course.student_group.user_set.add(user)

        #Create an Instructor User

        instructor = User.objects.create_user('Professor 1')
        instructor.set_password('class2go')
        instructor.save()
        course.instructor_group.user_set.add(instructor)

        #Create some Announcements

        title = 'Welcome to Natural Language Processing!'
        description = 'Welcome to the course! Check out the links to announcements, news events, assignments and grades.'
        save_announcement(instructor, course_id, access_id, title, description)

        title = 'Assignment 1 Out'
        description = 'The first assignment has been posted.  Visit the assignments link to see the list of assignments and instructions for each assignment.  Be sure to check the additional pages for additional help. If you have any question email us at nlp@stanford.edu.'
        save_announcement(instructor, course_id, access_id, title, description)

        title = 'Friday Lecture for 7/13 cancelled'
        description = 'Because this Friday is Friday the 13th, we do not want to take any chances so class is cancelled. Post any questions on the discussion forum if you have any questions'
        save_announcement(instructor, course_id, access_id, title, description)

        title = 'Lecture Room Moved'
        description = 'We will be moving the lecture room to the medical school. Sorry for any inconviniences. For those of you without a bike, I am even more sorry. See you next lecture!'
        save_announcement(instructor, course_id, access_id, title, description)

def save_video_topic(course_id, title):
    
        video_topic = VideoTopic(course_id = course_id,
                                  title = title)
        
        video_topic.save()

def save_video(course_id, topic_id, access_id, title, description):
        
        video = Video(course_id = course_id,
        topic_id = topic_id,
        access_id = access_id,
        title = title,
        description = description)        
        
        video.save()
        
def save_additional_page(course_id, access_id, write_access, title, description):
    
        additional_page = AdditionalPage(course_id = course_id,
                                         access_id = access_id,
                                         write_access = write_access,
                                         title = title,
                                         description = description)
        
        additional_page.save()

def save_announcement(owner, course_id, access_id, title, description):

        announcement = Announcement(owner = owner,
                                course_id = course_id,
                                access_id = access_id,
                                title = title,
                                description = description)

        announcement.save()
        
