# Create your views here.
from c2g.models import *
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect, HttpRequest
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
from courses.member_management.tasks import add_student_task, email_new_student_invite
import csv

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
    invites = StudentInvitation.objects.filter(course=course)
    per_page_str = request.GET.get('per_page', '25')
    page_str = request.GET.get('page')
    invite_page_str = request.GET.get('invite_page')
    
    try:
        per_page = int(per_page_str)
    except ValueError:
        #just go with the defaults here
        per_page = 25

    student_filter = request.GET.get('student_filter', '')
    if student_filter:
        students = students.filter(Q(username__icontains=student_filter) | Q(email__icontains=student_filter))

    num_students = students.count()

    paginator = Paginator(students, per_page)

    try:
        student_page = paginator.page(page_str)
    except PageNotAnInteger:
        student_page = paginator.page(1)
    except EmptyPage:
        student_page = paginator.page(paginator.num_pages)

    invite_filter = request.GET.get('invite_filter', '')
    if invite_filter:
        invites = invites.filter(email__icontains=invite_filter)

    num_invites = invites.count()

    invite_paginator = Paginator(invites, per_page)

    try:
        invite_page = invite_paginator.page(invite_page_str)
    except PageNotAnInteger:
        invite_page = invite_paginator.page(1)
    except EmptyPage:
        invite_page = invite_paginator.page(invite_paginator.num_pages)

    return render_to_response('member_management/list.html',
                                {'common_page_data':request.common_page_data,
                                 'course':course,
                                 'instructors':instructors,
                                 'tas':tas,
                                 'num_students':num_students,
                                 'student_page':student_page,
                                 'student_filter':student_filter,
                                 'num_invites':num_invites,
                                 'invite_page':invite_page,
                                 'invite_filter':invite_filter,
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

    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]) + "#students")


@require_POST
@auth_is_course_admin_view_wrapper
def reclassify_member(request, course_prefix, course_suffix):
    """This view allows course admins to reclassify a course member as a student/ta/readonly-ta/instructor"""
    course = request.common_page_data['course']
    username = request.POST.get('username')
    # will be one of "student", "instructor", "ta", "readonly_ta"
    to_group = request.POST.get('to_group')
    
    #validate username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Username "%s" does not correspond to a user in the system' % username)
        return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]) + "#students")
    if not is_member_of_course(course, user):
        messages.add_message(request, messages.ERROR, 'User "%s" is not a member of this course!' % username)
        return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]) + "#students")

    #validate to_group
    poss_groups = { "students" : course.student_group,
                    "instructors" : course.instructor_group,
                    "tas" : course.tas_group,
                    "readonly_tas" : course.readonly_tas_group
                  }

    if to_group not in poss_groups:
        messages.add_message(request, messages.ERROR, 'You have specified an invalid course role for this course member %s' % username)
        return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]) + "#students")

    for desc, group in poss_groups.iteritems():
        if to_group == desc:
            group.user_set.add(user)
        else:
            group.user_set.remove(user)

    messages.add_message(request, messages.INFO, 'Successfully made %s a %s for %s' % (username, to_group, course.title))
    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]) + "#" + to_group)




@require_POST
@auth_is_course_admin_view_wrapper
def resend_invite(request, course_prefix, course_suffix):
    """This view allows course admins to resend invitation emails"""
    course = request.common_page_data['course']
    email = request.POST.get('resend_email')
    invites = StudentInvitation.objects.filter(course=course, email=email)
    for invite in invites:
        email_new_student_invite(request, invite)
        messages.add_message(request, messages.INFO, 'Re-sent invitation email to %s' % email)
    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]) + "#invited")

@require_POST
@auth_is_course_admin_view_wrapper
def uninvite(request, course_prefix, course_suffix):
    """This view allows course admins to rescind invitations"""
    course = request.common_page_data['course']
    email = request.POST.get('uninvite_email')
    invites = StudentInvitation.objects.filter(course=course, email=email)
    for invite in invites:
        invite.delete()
        messages.add_message(request, messages.INFO, 'The invitation for %s to join this course has been rescinded' % email)
    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]) + "#invited")



@require_POST
@auth_is_course_admin_view_wrapper
def enroll_students(request, course_prefix, course_suffix):
    """This view allows course admins to enroll a single or a csv-batch of students"""
    course = request.common_page_data['course']
    send_email = request.POST.get('send_email')

    #If it's a CSV-file batch, use the helper
    if request.FILES:
        return csv_enroll_helper(request, course, send_email)

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

    #now actually add the student(s).
    add_student_task(request, course, new_student_email, send_email)

    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course_prefix, course_suffix]))


def csv_enroll_helper(request, course, send_email):
    """This helper function handles batch enrollment/inviting via a CSV file"""
    
    dummy_request = HttpRequest()
    dummy_request.META['HTTP_HOST'] = request.META['HTTP_HOST']
    
    if request.FILES:
        good_count=0;
        #We build up the records to be saved as a dict
        for f in request.FILES.itervalues():
            row_count=0;
            reader = csv.reader(f)
            for row in reader:  # each row should be: "<new_student_email>"
                row_count += 1
                valid, output = validate_row(row, row_count)
                if not valid:
                    messages.add_message(request, messages.WARNING, output)
                else:
                    add_student_task.delay(dummy_request, course, output, send_email, batched=True)
                    good_count += 1

        messages.add_message(request, messages.INFO, "Successfully queued %d students to be added" % good_count)
    return HttpResponseRedirect(reverse('courses.member_management.views.listAll', args=[course.prefix, course.suffix]))


def validate_row(row, row_num):
    """
        Helper function to validate a row read in from CSV.
        If validation fails, returns tuple of (False, error message).
        If validation succeeds, returns tuple of (True, email)
    """

    if not isinstance(row, list):
        return (False, "Badly formatted CSV row %d" % row_num)
    
    try:
        validate_email(row[0].strip())
    except ValidationError:
        return (False, "CSV row %d contains invalid email address: %s" % (row_num,row[0]))
                
    return (True, row[0].strip())



