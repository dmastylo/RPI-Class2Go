from celery import task
from django.contrib.auth.models import User
from courses.actions import is_member_of_course
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages
from django.core.urlresolvers import reverse
from c2g.models import Course, StudentInvitation
from urllib import quote_plus

import settings
import re

@task()
def add_student_task(request, course, new_student_email, send_email, batched=False):
    """
        This is a factored-out helper function that takes an email address of an
        invited student and determines whether to add the student to the course or
        send the student an email about creating an account, etc.
        
        This has been made into a celery task. Calling this task with
        using a dummy/stripped down request would be useful to reduce pickled
        datastructure size.  The task should be called with batched=True and
        a request that only needs to be used for build_absolute_uri 
        (has META['HTTP_HOST'])
    """
    #First search for matching students
    new_students = User.objects.filter(Q(username__iexact=new_student_email) | Q(email__iexact=new_student_email))
    if new_students.exists():
        #this is the case where we don't need to create users
        for student in new_students:
            if not is_member_of_course(course, student):
                course.student_group.user_set.add(student)
                if send_email:
                    email_existing_student_enrollment(request, course, student)
                if not batched:
                    messages.add_message(request, messages.INFO, 'Successfully enrolled student %s in course' % student.username)
            else:
                if not batched:
                    messages.add_message(request, messages.WARNING, 'Student %s is already a course member' % student.username)
    else:
        #this is the case where there is no existing user, so we send an invitation
        invite, created = StudentInvitation.objects.get_or_create(course=course, email=new_student_email)
        if created and not batched:
            messages.add_message(request, messages.INFO, 'Successfully invited student %s to create a Class2Go account for the course' \
                                 % new_student_email)
        elif not batched:
            messages.add_message(request, messages.WARNING, '%s has already been invited to the course.  An invitation email has been re-sent' \
                                 % new_student_email)
        
        #in the case of an invitation to create a new account, we have to send email no matter the checkbox
        email_new_student_invite(request,invite)


def email_new_student_invite(request, invite):
    course = invite.course
    email_text = render_to_string('member_management/student_invite.txt',
                                  {'title':course.title,
                                  'registration_url':request.build_absolute_uri(reverse('registration_register')) \
                                  + "?invite=%s" % quote_plus(invite.email),
                                  'course_url':request.build_absolute_uri(reverse('courses.views.main', args=[course.prefix, course.suffix])),
                                  'institution':settings.SITE_TITLE,
                                  'email':invite.email,
                                  })
    email_html = render_to_string('member_management/student_invite.html',
                                  {'title':course.title,
                                  'registration_url':request.build_absolute_uri(reverse('registration_register')) \
                                  + "?invite=%s" % quote_plus(invite.email),
                                  'course_url':request.build_absolute_uri(reverse('courses.views.main', args=[course.prefix, course.suffix])),
                                  'institution':settings.SITE_TITLE,
                                  'email':invite.email,
                                  })
    subject = "You have been invited to register for " + course.title
    
    staff_email = settings.SERVER_EMAIL
    course_title_no_quotes = re.sub(r'"', '', course.title) # strip out all quotes
    from_addr = '"%s" Course Staff <%s>' % (course_title_no_quotes, staff_email) #make certain that we quote the name part of the email address
    email_helper(subject, email_text, email_html, from_addr, invite.email)


def email_existing_student_enrollment(request, course, user):
    email_text = render_to_string('member_management/existing_student_enroll.txt',
                                  {'user':user,
                                  'title':course.title,
                                  'url':request.build_absolute_uri(reverse('courses.views.main', args=[course.prefix, course.suffix])),
                                  'institution':settings.SITE_TITLE,
                                  })
    email_html = render_to_string('member_management/existing_student_enroll.html',
                                  {'user':user,
                                  'title':course.title,
                                  'url':request.build_absolute_uri(reverse('courses.views.main', args=[course.prefix, course.suffix])),
                                  'institution':settings.SITE_TITLE,
                                  })
    subject = "You have been enrolled in " + course.title
    
    staff_email = settings.SERVER_EMAIL
    course_title_no_quotes = re.sub(r'"', '', course.title) # strip out all quotes
    from_addr = '"%s" Course Staff <%s>' % (course_title_no_quotes, staff_email) #make certain that we quote the name part of the email address
    email_helper(subject, email_text, email_html, from_addr, user.email)


def email_helper(subject, email_text, email_html, from_addr, to_addr):
    connection = get_connection() #get connection from settings
    connection.open()
    msg = EmailMultiAlternatives(subject, email_text, from_addr, [to_addr], connection=connection)
    msg.attach_alternative(email_html,'text/html')
    connection.send_messages([msg])
    connection.close()

