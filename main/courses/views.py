from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from c2g.models import *
from courses.course_materials import get_course_materials
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page

from courses.forms import *

from courses.actions import auth_view_wrapper

from c2g.models import CurrentTermMap
import settings, logging
import datetime


logger = logging.getLogger(__name__)


def index(item): # define a index function for list items
 return item[1]


curTerm = 'Fall2012'

def current_redirects(request, course_prefix):
    try:
        suffix = CurrentTermMap.objects.get(course_prefix=course_prefix).course_suffix
    except CurrentTermMap.DoesNotExist:
        suffix = curTerm # Use this as default fallback

    scheme='https://' if request.is_secure() else 'http://'

    if Course.objects.filter(handle=course_prefix+'--'+suffix).exists():
        if suffix == 'Fall2012': #send requests to Fall2012 classes under the new codebase back to the old codebase
            http_host=re.sub(r'class2go\.', 'class.', request.META['HTTP_HOST'], flags=re.I)
        else:  #send everyone else to the new codebase
            http_host=re.sub(r'class\.', 'class2go.', request.META['HTTP_HOST'], flags=re.I)
        return redirect(scheme+http_host+reverse('courses.views.main',args=[course_prefix, suffix]))
    else: 
        raise Http404
    

def main(request, course_prefix, course_suffix):
    #Common page data is already run in middleware
    #try:
    #    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    #except Course.DoesNotExist:
    #    raise Http404

    common_page_data=request.common_page_data
    ##JASON 9/5/12###
    ##For Launch, but I don't think it needs to be removed later##
    if common_page_data['course'].preview_only_mode:
        if not common_page_data['is_course_admin']:
            redir = reverse('courses.preview.views.preview',args=[course_prefix, course_suffix])
            if (settings.INSTANCE == 'stage' or settings.INSTANCE == 'prod'):
                redir = 'https://'+request.get_host()+redir
            return redirect(redir)

    course = common_page_data['course']
    announcement_list = Announcement.objects.getByCourse(course=common_page_data['course']).order_by('-time_created')[:11]
    if len(announcement_list) > 10:
        many_announcements = True
        announcement_list = announcement_list[0:10]
    else:
        many_announcements = False
    
    if request.user.is_authenticated():
        is_logged_in = 1
    else:
        is_logged_in = 0

    return render_to_response('courses/view.html',
            {'common_page_data':    common_page_data,
             'course':              course,
             'announcement_list':   announcement_list,
             'many_announcements':  many_announcements,
             'is_logged_in':        is_logged_in
             },
            context_instance=RequestContext(request))

def get_upcoming_exams(course):
  end_date = datetime.date.today() + datetime.timedelta(weeks=2)
  exams = Exam.objects.filter(
    course=course, 
    mode='ready',
    is_deleted=0,
    due_date__gte = datetime.date.today(),
    due_date__lte = end_date, 
    live_datetime__lte = datetime.date.today()
    ).order_by('due_date')
  return exams


@auth_view_wrapper
def course_materials(request, course_prefix, course_suffix, section_id=None):

    #Vars used for single section nav
    prev_section = None
    next_section = None

    if section_id:
        #If an instructor switches to edit view from a single section's materials page,
        #just redirect to display all sections, since section_id is for viewing sections in ready mode
        if request.common_page_data['course_mode'] == 'draft':
            return redirect('courses.views.course_materials', request.common_page_data['course_prefix'], request.common_page_data['course_suffix'])

        #Makes sure section_id is for a ready mode section
        try:
            section = ContentSection.objects.getByCourse(course=request.common_page_data['course']).get(pk=section_id)
        except ContentSection.DoesNotExist:
            raise Http404
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True, get_pset_content=False, get_additional_page_content=True, get_file_content=True, get_exam_content=True, SECTION=section)

        #Get prev/next nav links
        sections = request.common_page_data['content_sections']
        for index, item in enumerate(sections):
            if item == section:
                cur_index = index
                break

        if cur_index > 0:
            prev_section = sections[cur_index-1]
        if cur_index < len(sections) - 1:
            next_section = sections[cur_index+1]
    else:
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True, get_pset_content=False, get_additional_page_content=True, get_file_content=True, get_exam_content=True)

    form = None
    if request.common_page_data['course_mode'] == "draft":
        form = LiveDateForm()

    return render_to_response('courses/'+request.common_page_data['course_mode']+'/course_materials.html', {'common_page_data': request.common_page_data, 'section_structures':section_structures, 'context':'course_materials', 'form':form, 'prev_section':prev_section, 'next_section':next_section}, context_instance=RequestContext(request))

@cache_page(60*3, cache="view_store")
def leftnav(request, course_prefix, course_suffix):
    course = request.common_page_data['ready_course']
    full_contentsection_list, full_index_list = get_full_contentsection_list(course)
    return render_to_response('left_nav.html',
                              {
                              'PREFIX':              course_prefix,
                              'SUFFIX':              course_suffix,
                              'contentsection_list': full_contentsection_list,
                              'full_index_list':     full_index_list,
                              },
                              context_instance=RequestContext(request))


@cache_page(60*60, cache="view_store")
def rightnav(request, course_prefix, course_suffix):
  course = request.common_page_data['ready_course']
  exams = get_upcoming_exams(course)
  exams = [exam for exam in exams if not exam.is_child()]
  return render_to_response('right_nav.html',
                            {'common_page_data':   request.common_page_data,
                            'assignments':        exams, #setting to True to get consistent, ok to show anon users links
                            },
                            context_instance=RequestContext(request))


@auth_view_wrapper
@require_POST
@csrf_protect
def unenroll(request, course_prefix, course_suffix):
    
    try:
        course = Course.objects.get(handle=course_prefix+'--'+course_suffix, mode='ready')
    except Course.DoesNotExist:
        raise Http404
            
    student_group = Group.objects.get(id=course.student_group_id)
    student_group.user_set.remove(request.user)
    
    return redirect(request.META['HTTP_REFERER'])



def get_full_contentsection_list(course, filter_children=True):
    """Return a list of ContentSections with material and a list of all material for this course."""

    level2_items = {}                            # level2_items gets filled lazily
    groups_with_children = set([])               # ContentGroups that have level2 items
    
    def filter_level2_contentgroup_entries(t, i):
        if level2_items.has_key(t): return i not in level2_items[t]
        else:                       return True

    desired_item = lambda t,i: True
    if filter_children:
        desired_item = filter_level2_contentgroup_entries
        # There's some django magic about using QuerySet in this position that
        # make 1 query instead of hundreds
        cg2_list = ContentGroup.objects.filter(course=course, level=2)
        for cg2 in cg2_list:
            cg2_t = cg2.get_content_type()
            #Using a pattern where we access the foreignkey ids directly from the
            #ContentGroup object. "cg.exam_id".  The bad way is to
            #do something like "cg.exam.id", which dereferences the foreignkey
            #as a select
            level2_items.setdefault(cg2_t, set([])).add(cg2.get_content_id())
            groups_with_children.add(cg2.group_id)

    parent_cgos = list(ContentGroup.objects.filter(course=course, level=1, group_id__in=groups_with_children))
    parents_as_tuple = set(map(lambda cgo: (cgo.get_content_type(), cgo.get_content_id()), parent_cgos))

    tagged_object_lists = {}
    for tag, cls in ContentGroup.groupable_types.iteritems():
        tagged_object_lists[tag] = cls.objects.getByCourse(course=course)
    
    full_index_list = {}
    full_contentsection_list=[]

    for contentsection in ContentSection.objects.getByCourse(course=course):
        index_list = []
        cs_id      = contentsection.id
        for tag in ContentGroup.groupable_types.keys():
            for obj in [o for o in tagged_object_lists[tag] if o.section_id == cs_id]:
                if desired_item(tag, obj.id):
                    is_parent = (tag, obj.id) in parents_as_tuple
                    if tag == 'file':
                        index_list.append({ 'type': tag, 'ref': obj, 'icon': obj.get_icon_type(), 'is_parent':is_parent })
                    else:
                        index_list.append({ 'type': tag, 'ref': obj, 'icon': None, 'is_parent':is_parent })

        index_list = sorted(index_list, cmp=lambda x,y: -1 if x['ref'].index < y['ref'].index else +1)
        # NB: B/c of for loops above, index_list is sorted by index, then by type tag
        full_index_list[cs_id] = index_list
        if index_list:                           # don't show empty sections
            full_contentsection_list.append(contentsection)
    return full_contentsection_list, full_index_list

