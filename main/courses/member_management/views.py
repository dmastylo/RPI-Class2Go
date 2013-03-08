# Create your views here.
from c2g.models import *
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from courses.actions import auth_is_course_admin_view_wrapper, is_member_of_course
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail import send_mail

import settings
import re

@auth_is_course_admin_view_wrapper
def listAll(request, course_prefix, course_suffix):
    """
    This view can be used to list all members of a course.
    It will only paginate students.    
    """
    course = request.common_page_data['course']
    instructors = course.instructor_group.user_set.all()
    tas = course.tas_group.user_set.all()
    students = course.get_all_students().order_by('username')
    per_page_str = request.GET.get('per_page', '25')
    page_str = request.GET.get('page')
    
    try:
        per_page = int(per_page_str)
    except ValueError:
        #just go with the defaults here
        per_page = 25

    student_filter = request.GET.get('student_filter', '')
    if student_filter:
        students = students.filter(Q(username__icontains=student_filter) | Q(email__icontains=student_filter))

    paginator = Paginator(students, per_page)

    try:
        student_page = paginator.page(page_str)
    except PageNotAnInteger:
        student_page = paginator.page(1)
    except EmptyPage:
        student_page = paginator.page(paginator.num_pages)

    return render_to_response('member_management/list.html',
                                {'common_page_data':request.common_page_data,
                                 'course':course,
                                 'instructors':instructors,
                                 'tas':tas,
                                 'student_page':student_page,
                                 'student_filter':student_filter,
                                 'per_page':per_page},
                               context_instance=RequestContext(request))

@require_POST
@auth_is_course_admin_view_wrapper
def unenroll_student(request, course_prefix, course_suffix):
    """This view allows course admins to unenroll students"""
    course = request.common_page_data['course']
    username = request.POST.get('remove_username')
    try:
        student = User.objects.get(username=username)
        if course.student_group in student.groups.all():
            course.student_group.user_set.remove(student)
            messages.add_message(request, messages.INFO, 'Student %s has been removed from this course' % username)

    except User.DoesNotExist, User.MultipObjectsReturned:
        pass

    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]))


@require_POST
@auth_is_course_admin_view_wrapper
def enroll_students(request, course_prefix, course_suffix):
    """This view allows course admins to enroll a single or a csv-batch of students"""
    course = request.common_page_data['course']
    send_email = request.POST.get('send_email')

    #If it's a CSV-file batch, use the helper
    if request.FILES:
        return csv_enroll_helper(request, course)

    #a little bit of validation
    new_student_email = request.POST.get('new_email')
    if not new_student_email:
        messages.add_message(request, messages.ERROR, 'Please enter an email for the new student or choose a CSV file')
        return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]))

    new_student_email = new_student_email.strip()
    
    try:
        validate_email(new_student_email)
    except ValidationError:
        messages.add_message(request, messages.ERROR, 'Please enter a valid email for the new student')
        return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]))

    #now actually add the student(s).  First search for matching students
    new_students = User.objects.filter(Q(username__iexact=new_student_email) | Q(email__iexact=new_student_email))
    if new_students.exists():
        #this is the case where we don't need to create users
        for student in new_students:
            if not is_member_of_course(course, student):
                course.student_group.user_set.add(student)
                if send_email:
                    email_existing_student_enrollment(request, course, student)
                messages.add_message(request, messages.INFO, 'Successfully enrolled student %s in course' % student.username)
            else:
                messages.add_message(request, messages.WARNING, 'User %s is already a course member' % student.username)

    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]))


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

    staff_email = 'noreply@class2go.stanford.edu'
    course_title_no_quotes = re.sub(r'"', '', course.title) # strip out all quotes
    from_addr = '"%s" Course Staff <%s>' % (course_title_no_quotes, staff_email) #make certain that we quote the name part of the email address

    connection = get_connection() #get connection from settings
    connection.open()
    msg = EmailMultiAlternatives(subject, email_text, from_addr, [user.email], connection=connection)
    msg.attach_alternative(email_html,'text/html')
    connection.send_messages([msg])
    connection.close()


def csv_enroll_helper(request, course):
    return HTTPReponse('OK')
