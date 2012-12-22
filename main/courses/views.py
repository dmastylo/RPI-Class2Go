from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from courses.forms import *

from courses.actions import auth_view_wrapper

from c2g.models import CurrentTermMap
import settings


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

    
    announcement_list = Announcement.objects.getByCourse(course=common_page_data['course']).order_by('-time_created')[:11]
    if len(announcement_list) > 10:
        many_announcements = True
        announcement_list = announcement_list[0:10]
    else:
        many_announcements = False
    
    if request.user.is_authenticated():
        is_logged_in = 1
        news_list = common_page_data['ready_course'].newsevent_set.all().order_by('-time_created')[0:5]
    else:
        is_logged_in = 0
        news_list = []

    course = common_page_data['course']
    full_contentsection_list, full_index_list = get_full_contentsection_list(course)
    return render_to_response('courses/view.html',
            {'common_page_data':    common_page_data,
             'announcement_list':   announcement_list,
             'many_announcements':  many_announcements,
             'news_list':           news_list,
             'contentsection_list': full_contentsection_list,
             'video_list':          Video.objects.getByCourse(course=course),
             'pset_list':           ProblemSet.objects.getByCourse(course=course),
             'full_index_list':     full_index_list,
             'is_logged_in':        is_logged_in
             },
            context_instance=RequestContext(request))

@auth_view_wrapper
def course_materials(request, course_prefix, course_suffix):

    section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True, get_pset_content=False, get_additional_page_content=True, get_file_content=True, get_exam_content=True)

    form = None
    if request.common_page_data['course_mode'] == "draft":
        form = LiveDateForm()

    return render_to_response('courses/'+request.common_page_data['course_mode']+'/course_materials.html', {'common_page_data': request.common_page_data, 'section_structures':section_structures, 'context':'course_materials', 'form':form}, context_instance=RequestContext(request))

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

    def no_child_filter(t=None, i=None):
        return True

    level2_items = {}                            # level2_items gets filled lazily
    def working_child_filter(t, i):
        if len(level2_items) == 0:
            for cg2 in ContentGroup.objects.filter(course=course).filter(level=2):
                cg2_t = cg2.get_content_type()
                level2_items.setdefault(cg2_t, []).append(getattr(cg2, cg2_t).id)
        if level2_items.has_key(t): return i not in level2_items[t]
        else:                       return True

    desired_item = working_child_filter
    if not filter_children:
        desired_item = no_child_filter

    tagged_object_lists = {}
    for tag, cls in ContentGroup.groupable_types.iteritems():
        tagged_object_lists[tag] = cls.objects.getByCourse(course=course)
    
    full_index_list = []
    full_contentsection_list=[]

    for contentsection in ContentSection.objects.getByCourse(course=course):
    
        index_list = []
        cs_id      = contentsection.id
        for tag in ContentGroup.groupable_types.keys():
            for t in tagged_object_lists[tag].filter(section_id=cs_id):
                t_id = t.id
                if desired_item(tag, t_id):
                    if tag != 'file':
                        index_list.append((tag, t.index, t_id, cs_id, t.slug, t.title))
                    else:
                        icon_type = t.get_icon_type()
                        index_list.append((tag, t.index, t_id, cs_id, t.file.url, t.title, icon_type))

        full_index_list.append(sorted(index_list, key = index))
        if index_list:                           # don't show empty sections
            full_contentsection_list.append(contentsection)
    return full_contentsection_list, full_index_list

