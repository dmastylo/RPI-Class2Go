import datetime
import logging

from database import AWS_STORAGE_BUCKET_NAME
from django.core.cache import get_cache

from c2g.models import AdditionalPage, CacheStat, ContentSection, Course


logger=logging.getLogger(__name__)


def get_common_page_data(request, prefix, suffix):

    CACHE_STORE   = 'course_store'
    CACHE         = get_cache(CACHE_STORE)
    course_handle = prefix+"--"+suffix

    ready_course = Course.objects.get(handle=course_handle, mode='ready')
    draft_course = Course.objects.get(handle=course_handle, mode='draft')
    
    course_mode = 'ready'
    course = ready_course
    
    prefix = course.prefix
    suffix = course.suffix
    
    can_switch_mode = False
    is_course_admin = False
    is_course_member = False
    
    user_groups = request.user.groups.all()
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
    course_info_page_handle = course_handle + '_course_info_pages'
    course_info_pages = CACHE.get(course_info_page_handle)
    if course_info_pages:
        CacheStat.report('hit', CACHE_STORE)
    else:
        CacheStat.report('miss', CACHE_STORE)
        course_info_pages = AdditionalPage.objects.filter(course=course,is_deleted=0,menu_slug='course_info').order_by('index')
        CACHE.set(course_info_page_handle, course_info_pages)
    if view_mode != 'edit':
        course_info_pages = [page for page in course_info_pages if page.description]

    # Get list of non-empty content sections for course materials dropdown menu
    content_sections = None
    if course_mode == 'ready':
        content_section_page_handle = course_handle + '_nonempty_content_sections'
        content_sections = CACHE.get(content_section_page_handle)
        if content_sections:
            CacheStat.report('hit', CACHE_STORE)
        else:
            CacheStat.report('miss', CACHE_STORE)
            content_sections = [s for s in ContentSection.objects.getByCourse(course) if s.countChildren() > 0]
            CACHE.set(content_section_page_handle, content_sections)
    
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
