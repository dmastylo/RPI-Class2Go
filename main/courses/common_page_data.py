from c2g.models import Course, ContentSection, AdditionalPage
from django.contrib.auth.models import User, Group
import datetime
import logging
from database import AWS_STORAGE_BUCKET_NAME

logger=logging.getLogger(__name__)

def get_common_page_data(request, prefix, suffix):
    
    ready_course = Course.objects.get(handle=prefix+"--"+suffix, mode='ready')
    draft_course = Course.objects.get(handle=prefix+"--"+suffix, mode='draft')
    
    course_mode = 'ready'
    course = ready_course
    
    prefix = course.prefix
    suffix = course.suffix
    
    can_switch_mode = False
    is_course_admin = False
    is_course_member = False
    
    user_groups = request.user.groups.all()
    #logger.info("here")
    for g in user_groups:
        if g.id == course.student_group_id:
            is_course_member = True
            break
        
        if g.id == course.instructor_group_id:
            can_switch_mode = True
            is_course_admin = True
            is_course_member = True
            break
 
        if g.id == course.tas_group_id:
            can_switch_mode = True
            is_course_admin = True
            is_course_member = True
            break

        if g.id == course.readonly_tas_group_id:
            can_switch_mode = True
            is_course_member = True
            break
            
    
    if can_switch_mode and ('course_mode' in request.session) and (request.session['course_mode'] == 'draft'):
        course_mode = 'draft'
        course = draft_course
        
    # View mode
    if course_mode == 'draft':
        view_mode = 'edit'
        if request.GET.get('view_mode') and request.GET.get('view_mode') == 'preview':
            view_mode = 'view'
    else:
        view_mode = 'view'
    
    # Course info pages
    course_info_pages = []
    for page in AdditionalPage.objects.getByCourseAndMenuSlug(course=course, menu_slug='course_info').all():
        if view_mode == 'edit' or page.description:
            course_info_pages.append(page)

    content_sections = None
    if course_mode == 'ready':
        #Get list of non-empty content sections for course materials dropdown menu
        content_sections = [s for s in ContentSection.objects.getByCourse(course) if s.countChildren() > 0]
    
    current_datetime = datetime.datetime.now()
    effective_current_datetime = current_datetime
    
    page_data = {
        'request': request,
        'course': course,
        'ready_course': ready_course,
        'draft_course': draft_course,
        'course_prefix':prefix,
        'course_suffix':suffix,
        'course_mode':course_mode,
        'can_switch_mode':can_switch_mode,
        'is_course_admin':is_course_admin,
        'is_course_member':is_course_member,
        'view_mode': view_mode,
        'course_info_pages':course_info_pages,
        'content_sections':content_sections,
        'view_mode': view_mode,
        'current_datetime':current_datetime,
        'effective_current_datetime':effective_current_datetime,
        'aws_storage_bucket_name':AWS_STORAGE_BUCKET_NAME,
    }
    return page_data
