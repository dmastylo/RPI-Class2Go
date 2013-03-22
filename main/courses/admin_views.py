from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from django.contrib.auth.models import User,Group
from courses.common_page_data import get_common_page_data

from c2g.models import Course, Institution, AdditionalPage, CurrentTermMap
from random import randrange
import datetime
from courses.actions import auth_view_wrapper, auth_is_staff_view_wrapper

@auth_view_wrapper
def admin(request, course_prefix, course_suffix):
    try:
        common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    except:
        raise Http404

    return render_to_response('courses/admin.html', {'common_page_data':common_page_data}, context_instance=RequestContext(request))
        

def setup_course(handle, user, start_date, end_date, title, contact, term, year, prefix, suffix, 
                 twitter_tag, logo_filename, institution_only, pre_enroll_only, preview_only):
    
    # Verify that there is no course with the same handle
    num_courses_with_same_handle = Course.objects.filter(handle=handle).count()
    if num_courses_with_same_handle > 0:
        return HttpResponse('A course with the same prefix and suffix already exists. Please choose a different prefix and/or suffix.')
    
    #Create groups
    r = randrange(0,100000000)
    student_group = Group.objects.create(name="Student Group for class2go course " + handle + " %d" % r)
    instructor_group = Group.objects.create(name="Instructor Group for class2go course " + handle + " %d" % r)
    tas_group = Group.objects.create(name="TAS Group for class2go course " + handle + " %d" % r)
    readonly_tas_group = Group.objects.create(name="Readonly TAS Group for class2go course " + handle + " %d" % r)
    
    #Add the professor to the instructor group
    instructor_group.user_set.add(user)

    #Setup dates
    start_date_elements = start_date.split('-')
    start_date_month = int(start_date_elements[0])
    start_date_day = int(start_date_elements[1])
    start_date_year = int(start_date_elements[2])

    end_date_elements = end_date.split('-')
    end_date_month = int(end_date_elements[0])
    end_date_day = int(end_date_elements[1])
    end_date_year = int(end_date_elements[2])    
    
    #Get the !!!single!!! (Stanford) institution and relate the course to it.
    institution = Institution.objects.all()[0]
        
    # Create the course
    draft_course = Course(
            student_group_id = student_group.id,
            instructor_group_id = instructor_group.id,
            tas_group_id = tas_group.id,
            readonly_tas_group_id = readonly_tas_group.id,
            title = title,
            contact = contact,
            term = term,
            year = year,
            calendar_start = datetime.datetime(start_date_year, start_date_month, start_date_day),
            calendar_end = datetime.datetime(end_date_year, end_date_month, end_date_day),
            list_publicly = 0,
            mode='draft',
            handle=handle,
            institution_id = institution.id,
            twitter_tag = twitter_tag,
            logo = logo_filename,
            institution_only = True if institution_only else False,
            preenroll_only = True if pre_enroll_only else False,
            preview_only_mode = True if preview_only else False
        )
    draft_course.save()
    
    draft_course.create_ready_instance()
        
    op = AdditionalPage(
                        course=draft_course,
                        menu_slug='course_info',
                        title='Overview',
                        description='',
                        slug='overview',
                        index=0,
                        mode='draft',
                       )
    op.save()
    op.create_ready_instance()
    
    #Create the CurrentTermMap table entry (note we still do not automatically update the DNS in Route 53)
    redir_entry, created = CurrentTermMap.objects.get_or_create(course_prefix = prefix)
    redir_entry.course_suffix = suffix
    redir_entry.save()
    
    
@auth_is_staff_view_wrapper
def new(request):
    if request.method == 'POST':
        #inst_id = request.POST.get('institution')
        # We are disabling the institutions functionality temporarily
        
        prefix = request.POST.get('prefix')
        suffix = request.POST.get('suffix')        
        handle = prefix + '--' + suffix
        user = request.user
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        title = request.POST.get('title')
        contact = request.POST.get('contact')
        term = request.POST.get('term')
        year = int(request.POST.get('year'))
        twitter_tag = request.POST.get('twitter_tag')
        logo_filename = request.POST.get('logo_filename')
        institution_only = request.POST.get('institution_only')
        pre_enroll_only = request.POST.get('pre_enroll_only')
        preview_only = request.POST.get('preview_only')
                
        setup_course(handle, user, start_date, end_date, title, contact, term, year, 
                     prefix, suffix, twitter_tag, logo_filename, institution_only, pre_enroll_only, preview_only)


        request.session['course_mode'] = 'draft'
        return redirect('courses.views.main', course_prefix = request.POST.get('prefix'), course_suffix = request.POST.get('suffix'))
       
    # GET    
    else:
        now = datetime.datetime.now()
        date = "%02d-%02d-%04d" %(now.month, now.day, now.year)
        
        # List of institutions
        institutions = Institution.objects.all()
        
        return render_to_response('courses/new.html', {'request': request, 'date': date, 'institutions': institutions }, context_instance=RequestContext(request))
    