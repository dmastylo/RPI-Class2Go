from datetime import datetime

from django.db.models import Count

from c2g.models import *


def get_course_materials(common_page_data, get_video_content=False, get_pset_content=False, get_additional_page_content = False, get_file_content=False, get_exam_content=False, exam_types=[], SECTION=None):
    COURSE  = common_page_data['course']
    REQUEST = common_page_data['request']
    USER    = REQUEST.user
    section_structures = []

    if not USER.is_authenticated():
        return section_structures

    # Collect initial data
    pages  = []
    files  = []
    exams  = []
    videos = []
    if get_additional_page_content:
        pages = AdditionalPage.objects.getBySection(section=SECTION) if SECTION else AdditionalPage.objects.getByCourse(course=COURSE)
    if get_file_content:
        files = File.objects.getBySection(section=SECTION) if SECTION else File.objects.getByCourse(course=COURSE)
    if get_exam_content:
        exams = Exam.objects.getBySection(section=SECTION) if SECTION else Exam.objects.getByCourse(course=COURSE)
    if get_video_content:
        videos = Video.objects.getBySection(section=SECTION) if SECTION else Video.objects.getByCourse(course=COURSE)

    sections = [SECTION] if SECTION else ContentSection.objects.getByCourse(course=COURSE)

    # Collect contentgroup info for this course
    parentchilds, childparents = collect_contentgroup_data(COURSE, USER)

    # Do other pre-filtering before content section iteration
    if get_video_content and videos:
        # TODO: Cache these?
        video_list = [video.id for video in videos]
        videoToExs = VideoToExercise.objects.values('video').filter(video__in=video_list, is_deleted=0).annotate(dcount=Count('video'))
        videoToExs = dict([d.values() for d in videoToExs.values('video_id', 'dcount')]) # transform into dictionary keyed on video id
        if common_page_data['course_mode'] == 'ready':
            video_recs = VideoActivity.objects.filter(course=COURSE, student=USER, video__in=video_list)
            video_recs = dict([(d['video_id'], d) for d in video_recs.values()]) # transform into dictionary keyed on video id
            video_downloads = VideoDownload.objects.values('video').filter(course=COURSE, student=USER, video__in=video_list).annotate(dcount=Count('video'))
            video_downloads = dict([d.values() for d in video_downloads.values('video_id', 'dcount')]) # transform into dictionary keyed on video id

    user_records = None
    if get_exam_content and exams:
        if exam_types:
            exams = exams.filter(exam_type__in=exam_types)
        # TODO: it would be nice to do this as a select by section (with all sections if SECTION is empty) and rearrange as a dictionary keyed on section id, then dicts by exam id
        user_records = ExamRecord.objects.filter(course=COURSE, student=USER, complete=True).order_by('time_created')

    # Define a number of useful helper functions that curry this scope
    def get_item_by_type(obj, label, preModeSensitive=lambda d:d,
                                     postReadyModeWithChildren=lambda d:d,
                                     postModeSensitiveBeforeAppend=lambda d:d,):
        # TODO: move 'self' targeting down into templates, remove label: obj
        item = {'type':label, 'self': obj, label: obj, 'index': obj.index, 'is_child': False,}
        item = preModeSensitive(item)
        if common_page_data['course_mode'] == 'ready':
            key = (label, obj.id)
            item = postReadyModeWithChildren(item) 
        else:
            key = (label, obj.image.id)
            item['visible_status'] = get_live_datetime_for(obj)
        parent = childparents.get(key, False)
        if parent:
            item.update({'is_child': True, 'parent': parent, 'children': []})
        else:
            item.update({'is_child': False, 'parent': None, 'children': parentchilds.get(key, {}).get('group_children', [])})
        item = postModeSensitiveBeforeAppend(item)
        return item

    def _video_helper_calc_completion(item):
        # Calculate video completion percentage and attach record
        download_count = video_downloads.get(video.id, 0)
        if download_count > 0:
            item['completed_percent'] = 100.0
        else:
            video_rec = video_recs.get(video.id, False)
            if video_rec:
                item['video_rec'] = video_rec
                item['completed_percent'] = 100.0 * max(video_rec['start_seconds'], video_rec['max_end_seconds'])/ video.duration if video.duration else 0
        return item

    def _video_helper_add_numQuestions(item):
        # Attach number of exam questions to video
        item['numQuestions'] = videoToExs.get(video.id, 0)
        return item

    def _exam_helper_get_set_score(item):
        try:
            scoreobj = ExamScore.objects.filter(course=COURSE, exam=exam, student=USER).latest('time_created')
            has_score = True
            score = scoreobj.score
        except ExamScore.DoesNotExist:
            has_score = False
            score = 0
        item['has_score'] = has_score
        item['score'] = score
        return item

    # Do content section iteration. TODO: turn this into iteration over a dict by section id
    for section in sections:
        section_dict = {'section':section, 'items':[]}

        if get_additional_page_content:
            for page in pages:
                if page.section_id == section.id:
                    item = get_item_by_type(page, 'additional_page')
                    if item:
                        section_dict['items'].append(item)

        if get_file_content:
            for file in files:
                if file.section_id == section.id:
                    item = get_item_by_type(file, 'file')
                    if item:
                        section_dict['items'].append(item)

        if get_video_content:
            for video in videos:
                if video.section_id == section.id:
                    item = get_item_by_type(video, 'video', postReadyModeWithChildren=_video_helper_calc_completion, 
                                                            postModeSensitiveBeforeAppend=_video_helper_add_numQuestions)
                    if item:
                        section_dict['items'].append(item)

        if get_exam_content:
            if SECTION:
                user_records = ExamRecord.objects.filter(course=COURSE, exam__section=section, student=USER, complete=True).order_by('time_created')
            def _exam_helper_filter_store_records(item):
                item['records'] = user_records.filter(exam=exam) #might change this to a python list filter if want to trade db access for memory
                return item
            for exam in exams:
                if exam.section_id == section.id:
                    item = get_item_by_type(exam, 'exam', preModeSensitive=_exam_helper_get_set_score, 
                                                          postReadyModeWithChildren=_exam_helper_filter_store_records)
                    if item:
                        section_dict['items'].append(item)

        if common_page_data['course_mode'] == 'draft' or len(section_dict['items']) > 0:
            section_dict['items'] = sorted(section_dict['items'], key=lambda k: k['index'])
            section_structures.append(section_dict)

    return section_structures

def collect_contentgroup_data(course, user=None):
    """Memoize portions of the ContentGroup table in a convenient form."""
    def type_sorter(ci1, ci2):
        ci1_type = ci1['type']
        ci2_type = ci2['type']
        ci1_title = ci1['title']
        ci2_title = ci2['title']
        if ci1_type < ci2_type:
            return -1
        elif ci1_type > ci2_type:
            return +1
        else:
            # equal types, go by title
            if ci1_title < ci2_title:
                return -1
            elif ci1_title > ci2_title:
                return +1
            else:
                return 0

    def name_sorter(ci1, ci2):
        ci1_name = ci1['name']
        ci2_name = ci2['name']
        ci1_ext = ci1['ext']
        ci2_ext = ci2['ext']
        if ci1_name and ci2_name:
            if ci1_ext < ci2_ext:
                return -1
            elif ci1_ext > ci2_ext:
                return +1
            else:
                # equal extensions, go by filename
                if ci1_name < ci2_name:
                    return -1
                elif ci1_name > ci2_name:
                    return +1
                else:
                    return 0
        else:
            return 0

    parent2child = {}
    child2parent = {}
    if course.mode == 'draft':
        course = course.image
    for cgroup_parent_ref in ContentGroup.objects.getByCourseAndLevel(course, 1):
        info = {'group_children': {}}
        parent_tag = cgroup_parent_ref.get_content_type()
        parent_target = getattr(cgroup_parent_ref, parent_tag)
        info['content_group_id']= cgroup_parent_ref.group_id
        info['group_parent_tag']= parent_tag
        info['group_parent_ref']= parent_target
        info['group_parent_id'] = parent_target.id
        parent_key_tuple = (info['group_parent_tag'], info['group_parent_id'])
        # Filter deleted parents and all of their children (they shouldn't have any)
        # Leave non-live parents displayed, because parent iteration is a matter for draft mode
        if parent_target.is_deleted == 1:
            continue
        for cgo in ContentGroup.objects.filter(group_id=cgroup_parent_ref.group_id, level=2):
            cttag = cgo.get_content_type()
            target = getattr(cgo, cttag)
            # Filter deleted children without worrying about who their parent is
            if target.is_deleted == 1:
                continue 
            child2parent[(cttag, target.id)] = parent_target
            # Filter non-live mode children from parent2child because it's child list is only iterated in ready mode
            if not target.is_live():
                continue
            if not cttag or not target:
                continue
            display = cgo.display_style or 'list'
            augmented_data = child_data_to_dict(cgo, cttag, target, user)
            if info['group_children'].has_key(display):
                info['group_children'][display].append(augmented_data)
            else:
                info['group_children'][display] = [augmented_data]
        # Sort the children within display type by type, then name
        for display in info['group_children']:
            info['group_children'][display] = sorted(sorted(info['group_children'][display], type_sorter), name_sorter)
        parent2child[parent_key_tuple] = info 
    return (parent2child, child2parent)

def child_data_to_dict(groupobj, cgtype, ref, user=None):
    # TODO: what we're doing here is abominable and can be considerably cleaned
    #       or removed altogether after the templates get tidied up.
    class NoFile():
        name = ''
    tmp_f  = getattr(ref, 'file', NoFile())
    name   = tmp_f.name.split('/').pop() if tmp_f else ''
    ext    = name.split('.').pop().lower() if tmp_f else ''
    #              target             target        this entry    target ref  
    child_data = {'type': cgtype, 'id': ref.id, 'self': groupobj, 'ref': ref, 'display': groupobj.display_style, 'ext': ext,
                  'name': name, 'title': ref.title, 'url': ref.get_url(), 'index': ref.index, 'children': None, }
    child_data[cgtype] = ref      # TODO: set 'exam':exam - remove after making templates use 'ref'
    if cgtype == "exam" and user: # TODO: per-type special cases belong somewhere else?
        child_data['records'] = ExamRecord.objects.filter(course=ref.course, student=user, complete=True, exam=ref)
    return child_data
    
def get_live_datetime_for(thing):
    """Return the appropriate .live_datetime string for thing"""
    prod_thing = getattr(thing, 'image', None)
    if prod_thing == None:
        return "<span style='color:#Ac7000;'>Error: No Live Mode Object</span>"
    if not prod_thing.live_datetime:
        return "<span style='color:#A00000;'>Not Live</span>"
    elif prod_thing.live_datetime > datetime.now():
        return prod_thing.live_datetime.strftime("<span style='color:#A07000;'>Live %F at %H:%M</span>" )
    else:
        return "<span style='color:green;'>Live</span>"

