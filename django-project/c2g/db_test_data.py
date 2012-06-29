from c2g.models import *
from django.contrib.auth.models import User,Group


def delete_db_data():

    #Since all tables are foreign key related, this deletes all data in all c2g tables
    Institution.objects.all().delete()

    # Nuke the django tables
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

                #Create the Group
                group = Group.objects.create(name="Group for class2go course " + code + str(institution.id))

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
                                group_id = group.id)

                course.save()

                if create_user_data == 1:
                    for q in range(0,10):

                        #Create the user
                        user = User.objects.create_user('test_' + str(course.id) + '_' + str(q))
                        group.user_set.add(user)
