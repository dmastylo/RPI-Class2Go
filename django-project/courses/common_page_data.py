from c2g.models import Course, AdditionalPage
from django.contrib.auth.models import User, Group
import datetime

def get_common_page_data(request, prefix, suffix):
    
    production_course = Course.objects.get(handle=prefix+"-"+suffix, mode='production')
    staging_course = Course.objects.get(handle=prefix+"-"+suffix, mode='staging')
    
    course_mode = 'production'
    course = production_course
    
    can_switch_mode = False
    is_course_admin = False
    
    user_groups = request.user.groups.all()
    for g in user_groups:
        if g.id == course.instructor_group_id or g.id == course.tas_group_id or g.id == course.readonly_tas_group_id:
            can_switch_mode = True
            break
            
    for g in user_groups:
        if g.id == production_course.instructor_group_id or g.id == production_course.tas_group_id:
            is_course_admin = True
            break
    
    if can_switch_mode and ('course_mode' in request.session) and (request.session['course_mode'] == 'staging'):
        course_mode = 'staging'
        course = staging_course
        
    # View mode
    if course_mode == 'staging':
        view_mode = 'edit'
        if request.GET.get('view_mode') and request.GET.get('view_mode') == 'preview':
            view_mode = 'view'
    else:
        view_mode = 'view'
    
    # Course info pages
    course_info_pages = AdditionalPage.objects.filter(course=course).order_by('index')
        
    current_datetime = datetime.datetime.now()
    effective_current_datetime = current_datetime
    
    page_data = {
        'request': request,
        'course': course,
        'production_course': production_course,
        'staging_course': staging_course,
        'course_prefix':prefix,
        'course_suffix':suffix,
        'course_mode':course_mode,
        'can_switch_mode':can_switch_mode,
        'is_course_admin':is_course_admin,
        'view_mode': view_mode,
        'course_info_pages':course_info_pages,
        'view_mode': view_mode,
        'current_datetime':current_datetime,
        'effective_current_datetime':effective_current_datetime
    }
    return page_data