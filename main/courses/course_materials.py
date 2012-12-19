from c2g.models import *
import datetime
from django.db.models import Count, Max
from django.db import connection


def get_course_materials(common_page_data, get_video_content=False, get_pset_content=False, get_additional_page_content = False, get_file_content=False, get_exam_content=False, exam_types=[]):
    COURSE  = common_page_data['course']
    REQUEST = common_page_data['request']
    USER    = REQUEST.user
    section_structures = []
    if USER.is_authenticated():
        sections = ContentSection.objects.getByCourse(course=COURSE)
        pages = AdditionalPage.objects.getByCourse(course=COURSE)
        files = File.objects.getByCourse(course=COURSE)
        exams = Exam.objects.getByCourse(course=COURSE)
        if exam_types:
            exams = exams.filter(exam_type__in=exam_types)
        l1items, l2items = get_contentgroup_data(COURSE)

        if get_video_content:
            videos = Video.objects.getByCourse(course=COURSE)
            if videos:
                video_list = []
                for video in videos:
                    video_list.append(video.id)
                videoToExs = VideoToExercise.objects.values('video').filter(video__in=video_list, is_deleted=0).annotate(dcount=Count('video'))
                    
                if common_page_data['course_mode'] == 'ready':
                    video_recs = VideoActivity.objects.filter(course=COURSE, student=USER)
                    video_downloads = VideoDownload.objects.values('video').filter(course=COURSE, student=USER).annotate(dcount=Count('video'))

        if get_pset_content:
            
            problem_sets = ProblemSet.objects.getByCourse(course=COURSE)
            if problem_sets:
                problem_set_list = []
                for problem_set in problem_sets:
                    problem_set_list.append(problem_set.id)
                psetToExs = ProblemSetToExercise.objects.values('problemSet').filter(problemSet__in=problem_set_list, is_deleted=0).annotate(dcount=Count('problemSet'))

                if common_page_data['course_mode'] == 'ready':
                    pset_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter(problemset_to_exercise__problemSet_id__in=problem_set_list, student=USER).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'))
                    
                    cursor = connection.cursor()
                    #The following 2 sqls are the same except the first is for a list of 2 or more and the second is for
                    # a single item. I was not able to construct the argument for a single value without it putting quotes 
                    # around the strings.
                    if len(problem_set_list) > 1:
                        cursor.execute("select e.fileName, p2e.problemSet_id, \
                                        count(case when p2e.is_deleted = 0 then 1 else null end) as `num_active` \
                                        from c2g_problemset_to_exercise p2e, c2g_exercises e \
                                        where p2e.exercise_id = e.id \
                                        and p2e.problemSet_id in %s \
                                        and p2e.mode = 'ready' \
                                        group by e.filename, p2e.problemSet_id \
                                        having num_active = 0", [tuple(problem_set_list)])
                    else:
                        cursor.execute("select e.fileName, p2e.problemSet_id, \
                                        count(case when p2e.is_deleted = 0 then 1 else null end) as `num_active` \
                                        from c2g_problemset_to_exercise p2e, c2g_exercises e \
                                        where p2e.exercise_id = e.id \
                                        and p2e.problemSet_id = %s \
                                        and p2e.mode = 'ready' \
                                        group by e.filename, p2e.problemSet_id \
                                        having num_active = 0", [problem_set_list[0]])

                    deleted_exercise_list = []
                    for row in cursor.fetchall():
                        filename = row[0]
                        problemset_id = row[1]
                                    
                        filename_item = {'filename' : filename,
                                         'problemset_id' : problemset_id
                                        }
                        deleted_exercise_list.append(filename_item)                    
                    
                    #This was close but not quite; couldn't include the case statement for resiliance to bad activity data.
                    #pset_score_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__problemSet__resubmission_penalty', 'problemset_to_exercise__problemSet__partial_credit_deadline', 'problemset_to_exercise__problemSet__grace_period', 'problemset_to_exercise__problemSet__late_penalty', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter( Q(problemset_to_exercise__problemSet_id__in=problem_set_list), Q(student=common_page_data['request'].user), (Q(problemset_to_exercise__problemSet__submissions_permitted=0) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created'))) | (Q(problemset_to_exercise__problemSet__submissions_permitted__gt=0) & Q(problemset_to_exercise__problemSet__submissions_permitted__gte=F('attempt_number')) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created')))).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'), last_valid_attempt_time=Max('time_created'))
                    
                    #The following 2 sqls are the same except the first is for a list of 2 or more and the second is for
                    # a single item. I was not able to construct the argument for a single value without it putting quotes 
                    # around the strings.                    
                    if len(problem_set_list) > 1:
                        cursor.execute("SELECT `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, `c2g_problem_sets`.`partial_credit_deadline`,  \
                                        `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName`, \
                                        count(`c2g_problem_activity`.`attempt_number`) AS `num_attempts`, \
                                        MAX(`c2g_problem_activity`.`time_created`) AS `last_valid_attempt_time`, \
                                        MAX(`c2g_problem_activity`.`complete`) AS `correct`, \
                                        min(case when c2g_problem_activity.complete = 1 then c2g_problem_activity.id else null end) as `first_correct_answer`, \
                                        max(c2g_problem_activity.id) as `max_activity_id` \
                                        FROM `c2g_problem_activity` \
                                        LEFT OUTER JOIN `c2g_problemset_to_exercise` ON (`c2g_problem_activity`.`problemset_to_exercise_id` = `c2g_problemset_to_exercise`.`id`) \
                                        INNER JOIN `c2g_problem_sets` ON (`c2g_problemset_to_exercise`.`problemSet_id` = `c2g_problem_sets`.`id`) \
                                        INNER JOIN `c2g_exercises` ON (`c2g_problemset_to_exercise`.`exercise_id` = `c2g_exercises`.`id`) \
                                        WHERE (`c2g_problem_activity`.`student_id` = %s AND `c2g_problemset_to_exercise`.`problemSet_id` IN %s \
                                        AND ((`c2g_problem_sets`.`submissions_permitted` = 0  AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`) \
                                        OR (`c2g_problem_sets`.`submissions_permitted` > 0  AND `c2g_problem_sets`.`submissions_permitted` >=  `c2g_problem_activity`.`attempt_number` \
                                        AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`))) \
                                        GROUP BY `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, \
                                        `c2g_problem_sets`.`partial_credit_deadline`, `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName` \
                                        ORDER BY NULL", [common_page_data['request'].user.id, tuple(problem_set_list)])
                    else:
                        cursor.execute("SELECT `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, `c2g_problem_sets`.`partial_credit_deadline`,  \
                                        `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName`, \
                                        count(`c2g_problem_activity`.`attempt_number`) AS `num_attempts`, \
                                        MAX(`c2g_problem_activity`.`time_created`) AS `last_valid_attempt_time`, \
                                        MAX(`c2g_problem_activity`.`complete`) AS `correct`, \
                                        min(case when c2g_problem_activity.complete = 1 then c2g_problem_activity.id else null end) as `first_correct_answer`, \
                                        max(c2g_problem_activity.id) as `max_activity_id` \
                                        FROM `c2g_problem_activity` \
                                        LEFT OUTER JOIN `c2g_problemset_to_exercise` ON (`c2g_problem_activity`.`problemset_to_exercise_id` = `c2g_problemset_to_exercise`.`id`) \
                                        INNER JOIN `c2g_problem_sets` ON (`c2g_problemset_to_exercise`.`problemSet_id` = `c2g_problem_sets`.`id`) \
                                        INNER JOIN `c2g_exercises` ON (`c2g_problemset_to_exercise`.`exercise_id` = `c2g_exercises`.`id`) \
                                        WHERE (`c2g_problem_activity`.`student_id` = %s AND `c2g_problemset_to_exercise`.`problemSet_id` = %s \
                                        AND ((`c2g_problem_sets`.`submissions_permitted` = 0  AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`) \
                                        OR (`c2g_problem_sets`.`submissions_permitted` > 0  AND `c2g_problem_sets`.`submissions_permitted` >=  `c2g_problem_activity`.`attempt_number` \
                                        AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`))) \
                                        GROUP BY `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, \
                                        `c2g_problem_sets`.`partial_credit_deadline`, `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName` \
                                        ORDER BY NULL", [common_page_data['request'].user.id, problem_set_list[0]])

                    score_list = []
                    for row in cursor.fetchall():
                        problemset_id = row[0]
                        submissions_permitted = row[1]
                        resubmission_penalty = row[2]
                        partial_credit_deadline = row[3]
                        grace_period = row[4]
                        late_penalty = row[5]
                        filename = row[6]
                        num_attempts = row[7]
                        last_valid_attempt_time = row[8]
                        correct = row[9]
                        first_correct_answer = row[10]
                        max_activity_id = row[11]                                
                                
                        score_item = {'problemset_id' : problemset_id,
                                      'submissions_permitted' : submissions_permitted,
                                      'resubmission_penalty' : resubmission_penalty,
                                      'partial_credit_deadline' : partial_credit_deadline,
                                      'grace_period' : grace_period,
                                      'late_penalty' : late_penalty,
                                      'filename' : filename,
                                      'num_attempts' : num_attempts,
                                      'last_valid_attempt_time' : last_valid_attempt_time,
                                      'correct' : correct,
                                      'first_correct_answer' : first_correct_answer,
                                      'max_activity_id' : max_activity_id
                                     }
                        score_list.append(score_item)

        index = 0
        for section in sections:
            section_dict = {'section':section, 'items':[]}

            if get_additional_page_content:
                for page in pages:
                    key = ('additional_page', page.id)
                    if page.section_id == section.id and not l2items.has_key(key):
                        children = get_children_by_display_style(key, l1items, l2items, USER)
                        
                        item = {'type':'additional_page', 'additional_page':page, 'index':page.index, 'children': children}

                        if common_page_data['course_mode'] == 'draft':
                            item['visible_status'] = get_live_datetime_for(page)
                        section_dict['items'].append(item)

            if get_file_content:
                for file in files:
                    key = ('file', file.id)
                    if file.section_id == section.id and not l2items.has_key(key):
                        children = get_children_by_display_style(key, l1items, l2items, USER)
                        
                        item = {'type':'file', 'file':file, 'index':file.index, 'children': children}

                        if common_page_data['course_mode'] == 'draft':
                            item['visible_status'] = get_live_datetime_for(file)
                        section_dict['items'].append(item)

            if get_video_content:
                        
                for video in videos:
                    key = ('video', video.id)
                    if video.section_id == section.id and not l2items.has_key(key):
                        children = get_children_by_display_style(key, l1items, l2items, USER)
                                
                        item = {'type':'video', 'video':video, 'completed_percent': 0, 'index':video.index, 'children': children}

                        numQuestions = 0
                        for videoToEx in videoToExs:
                            if videoToEx['video'] == video.id:
                                numQuestions = videoToEx['dcount']
                                break
                        
                        if common_page_data['course_mode'] == 'draft':
                            item['visible_status'] = get_live_datetime_for(video)
                        else:
                            download_count = 0
                            for video_download in video_downloads:
                                if video_download['video'] == video.id:
                                    download_count = video_download['dcount']
                                    break                                
                            
                            if download_count > 0:
                                item['completed_percent'] = 100.0
                            else:
                                for video_rec in video_recs:
                                    if video_rec.video_id == video.id:
                                        item['video_rec'] = video_rec
                                        if video.duration:
                                            item['completed_percent'] = 100.0 * max(video_rec.start_seconds, video_rec.max_end_seconds)/ video.duration
                                        else:
                                            item['completed_percent'] = 0

                        item['numQuestions'] = numQuestions
                        section_dict['items'].append(item)

            if get_pset_content:
                for problem_set in problem_sets:
                    key = ('problemSet', problem_set.id)
                    if problem_set.section_id == section.id and not l2items.has_key(key):
                        children = get_children_by_display_style(key, l1items, l2items, USER)
                        
                        item = {'type':'problem_set', 'problem_set':problem_set, 'index':problem_set.index, 'children': children}

                        numQuestions = 0
                        for psetToEx in psetToExs:
                            if psetToEx['problemSet'] == problem_set.id:
                                numQuestions = psetToEx['dcount']
                                break                            
                            
                        if common_page_data['course_mode'] == 'draft':
                            item['visible_status'] = get_live_datetime_for(problem_set)
                        else:
                            numCompleted = 0
                            for pset_activity in pset_activities:
                                if pset_activity['problemset_to_exercise__problemSet_id'] == problem_set.id and not filename_in_deleted_list(pset_activity['problemset_to_exercise__exercise__fileName'], problem_set.id, deleted_exercise_list):
                                    if pset_activity['correct'] == 1:
                                        numCompleted += 1
                                    elif pset_activity['problemset_to_exercise__problemSet__submissions_permitted'] != 0 and pset_activity['num_attempts'] >= pset_activity['problemset_to_exercise__problemSet__submissions_permitted']:
                                        numCompleted +=1                            

                            score = 0.0
                            for score_item in score_list:
                                problemset_id = score_item['problemset_id']
                                submissions_permitted = score_item['submissions_permitted']
                                resubmission_penalty = score_item['resubmission_penalty']
                                partial_credit_deadline = score_item['partial_credit_deadline']
                                grace_period = score_item['grace_period']
                                late_penalty = score_item['late_penalty']
                                filename = score_item['filename']
                                num_attempts = score_item['num_attempts']
                                last_valid_attempt_time = score_item['last_valid_attempt_time']
                                correct = score_item['correct']
                                first_correct_answer = score_item['first_correct_answer']
                                max_activity_id = score_item['max_activity_id']
                                
                                if problemset_id == problem_set.id and not filename_in_deleted_list(filename, problemset_id, deleted_exercise_list):
                                    exercise_percent = 100
                                    if first_correct_answer == None or first_correct_answer == max_activity_id:
                                                                                        
                                        if correct == 0:
                                            exercise_percent = 0
                                        else:
                                            exercise_percent -= resubmission_penalty*(num_attempts -1)

                                            if last_valid_attempt_time > grace_period:
                                                exercise_percent = int(exercise_percent*(100 - late_penalty)/100.0)
                            
                                        #floor exercise percent at 0
                                        exercise_percent = max(exercise_percent,0)
            
                                        #add to total_score
                                        score += exercise_percent/100.0
                            
                                    else:
                                        score = problem_set.get_score(USER)
                                        break

                            #Divide by zero safety check
                            if numQuestions == 0:
                                progress = 0
                            else:
                                progress = 100.0*numCompleted/numQuestions
                                
                            item['numCompleted'] = numCompleted
                            item['score'] = score
                            item['progress'] = progress

                        item['numQuestions'] = numQuestions
                        section_dict['items'].append(item)

            if get_exam_content:
                user_records = ExamRecord.objects.filter(course=COURSE, student=USER, complete=True).order_by('time_created')
                for exam in exams:
                    key = ('exam', exam.id)
                    if exam.section_id == section.id and not l2items.has_key(key):
                        exam_user_records = user_records.filter(exam=exam) #might change this to a python list filter if want to trade db access for memory
                        children = get_children_by_display_style(key, l1items, l2items, USER)
                        
                        item = {'type':'exam', 'exam':exam, 'index':exam.index, 'children': children, 'records':exam_user_records}
                        section_dict['items'].append(item)
                        
                        if common_page_data['course_mode'] == 'draft':
                            item['visible_status'] = get_live_datetime_for(exam)

            if common_page_data['course_mode'] == 'draft' or len(section_dict['items']) > 0:
                section_dict['items'] = sorted(section_dict['items'], key=lambda k: k['index'])
                section_structures.append(section_dict)
                index += 1

    return section_structures

def filename_in_deleted_list(filename, problem_set_id, deleted_exercise_list):
    for item in deleted_exercise_list:
        if item['filename'] == filename and item['problemset_id'] == problem_set_id:
            return True
    return False

def get_contentgroup_data(course):
    l1_items = {}
    l2_items = {}
    for cgtype, cgtid, cgref, target, level, display in [get_group_item_data(x, selfref=True) for x in 
                                                            ContentGroup.objects.getByCourse(course=course)]:
        if not target.is_live() or target.is_deleted:
            continue
        if level == 2:
            l2_items[(cgtype, cgtid)] = (cgref, target, level, display)
        else:
            l1_items[(cgtype, cgtid)] = cgref.group_id
    return l1_items, l2_items

def get_group_item_data(group_item, selfref=False):
    ctype   = group_item.get_content_type()
    level   = group_item.level
    display = group_item.display_style or 'button'
    target  = getattr(group_item, ctype)
    cgid    = target.id
    if not selfref:
        return ctype, cgid, target, level, display
    return ctype, cgid, group_item, target, level, display

def get_children_by_display_style(key, level1_items, level2_items, user=None):
    children = get_children(key, level1_items, level2_items, user)
    tagged_children = {}
    for child in children:
        display_style = child.get('display', 'button')
        if not tagged_children.has_key(display_style):
            tagged_children[display_style] = [child]
        else:
            tagged_children[display_style].append(child)
    return tagged_children

def get_children(key, level1_items, level2_items, user=None):

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

    children = []
    if level1_items.has_key(key):
        group_id = level1_items[key]
        children.extend([augment_child_data(k, v, user) for k,v in level2_items.items() if v[0].group_id == group_id])
        children = sorted(sorted(children, type_sorter), name_sorter)
    return children

def augment_child_data(key, value, user=None):
    class NoFile():
        name = ''
    cgtype = key[0]
    ref    = value[1]
    tmp_f  = getattr(ref, 'file', NoFile())
    name   = tmp_f.name.split('/').pop()
    ext    = name.split('.').pop().lower()

    #              target             target        this entry    target ref  
    child_data = {'type': cgtype, 'id': key[1], 'self': value[0], 'ref': ref, 'display': value[3], 'ext': ext,
                  'name': name, 'title': ref.title, 'url': ref.get_url(), 'index': ref.index, 'children': None, }
    child_data[cgtype] = ref      # FIXME: set 'exam':exam - remove after making templates use 'ref'
    if cgtype == "exam" and user: # FIXME: per-type special cases belong somewhere else?
        child_data['records'] = ExamRecord.objects.filter(course=ref.course, student=user, complete=True, exam=ref)
    return child_data
    
def get_live_datetime_for(thing):
    """Return the appropriate .live_datetime string for thing"""
    prod_thing = getattr(thing, 'image', None)
    if prod_thing == None:
        return "<span style='color:#Ac7000;'>Error: No Live Mode Object</span>"
    if not prod_thing.live_datetime:
        return "<span style='color:#A00000;'>Not Live</span>"
    elif prod_thing.live_datetime > datetime.datetime.now():
        return prod_thing.live_datetime.strftime("<span style='color:#A07000;'>Live %F at %H:%M</span>" )
    else:
        return "<span style='color:green;'>Live</span>"


#Test purposes only - not to be run in production
def test_for_pset_progress_and_score(): 
    
    logfile = open('zzzz.log', 'w')
    
    #Get all courses
    courses = Course.objects.filter(mode='ready')
    
    #Get all users
    users = User.objects.all()
    
    for course in courses:
        logfile.write("course_id : " + str(course.id) + "\n")
        
        #Get all problemsets
        problem_sets = ProblemSet.objects.getByCourse(course=course)
        
        #Get all sections
        sections = ContentSection.objects.getByCourse(course=course)

        if problem_sets:
                    problem_set_list = []
                    for problem_set in problem_sets:
                        problem_set_list.append(problem_set.id)                        
                        
                        psetToExs = ProblemSetToExercise.objects.values('problemSet').filter(problemSet__in=problem_set_list, is_deleted=0).annotate(dcount=Count('problemSet'))

                    cursor = connection.cursor()
                    
                    if len(problem_set_list) > 1:
                        cursor.execute("select e.fileName, p2e.problemSet_id, \
                                        count(case when p2e.is_deleted = 0 then 1 else null end) as `num_active` \
                                        from c2g_problemset_to_exercise p2e, c2g_exercises e \
                                        where p2e.exercise_id = e.id \
                                        and p2e.problemSet_id in %s \
                                        and p2e.mode = 'ready' \
                                        group by e.filename, p2e.problemSet_id \
                                        having num_active = 0", [tuple(problem_set_list)])
                    else:
                        cursor.execute("select e.fileName, p2e.problemSet_id, \
                                        count(case when p2e.is_deleted = 0 then 1 else null end) as `num_active` \
                                        from c2g_problemset_to_exercise p2e, c2g_exercises e \
                                        where p2e.exercise_id = e.id \
                                        and p2e.problemSet_id = %s \
                                        and p2e.mode = 'ready' \
                                        group by e.filename, p2e.problemSet_id \
                                        having num_active = 0", [problem_set_list[0]])

                    deleted_exercise_list = []
                    for row in cursor.fetchall():
                        filename = row[0]
                        problemset_id = row[1]
                                    
                        filename_item = {'filename' : filename,
                                         'problemset_id' : problemset_id
                                        }

                        deleted_exercise_list.append(filename_item)

                    for user in users:
                        user_groups = user.groups.all()
                        for g in user_groups:
                            if g.id == course.student_group_id:
                                
                                pset_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter(problemset_to_exercise__problemSet_id__in=problem_set_list, student=user).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'))
                                #pset_score_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__problemSet__resubmission_penalty', 'problemset_to_exercise__problemSet__partial_credit_deadline', 'problemset_to_exercise__problemSet__grace_period', 'problemset_to_exercise__problemSet__late_penalty', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter( Q(problemset_to_exercise__problemSet_id__in=problem_set_list), Q(student=user), (Q(problemset_to_exercise__problemSet__submissions_permitted=0) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created'))) | (Q(problemset_to_exercise__problemSet__submissions_permitted__gt=0) & Q(problemset_to_exercise__problemSet__submissions_permitted__gte=F('attempt_number')) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created')))).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'), last_valid_attempt_time=Max('time_created'))

                                if len(problem_set_list) > 1:
                                    cursor.execute("SELECT `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, `c2g_problem_sets`.`partial_credit_deadline`,  \
                                                   `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName`, \
                                                    count(`c2g_problem_activity`.`attempt_number`) AS `num_attempts`, \
                                                    MAX(`c2g_problem_activity`.`time_created`) AS `last_valid_attempt_time`, \
                                                    MAX(`c2g_problem_activity`.`complete`) AS `correct`, \
                                                    min(case when c2g_problem_activity.complete = 1 then c2g_problem_activity.id else null end) as `first_correct_answer`, \
                                                    max(c2g_problem_activity.id) as `max_activity_id` \
                                                    FROM `c2g_problem_activity` \
                                                    LEFT OUTER JOIN `c2g_problemset_to_exercise` ON (`c2g_problem_activity`.`problemset_to_exercise_id` = `c2g_problemset_to_exercise`.`id`) \
                                                    INNER JOIN `c2g_problem_sets` ON (`c2g_problemset_to_exercise`.`problemSet_id` = `c2g_problem_sets`.`id`) \
                                                    INNER JOIN `c2g_exercises` ON (`c2g_problemset_to_exercise`.`exercise_id` = `c2g_exercises`.`id`) \
                                                    WHERE (`c2g_problem_activity`.`student_id` = %s AND `c2g_problemset_to_exercise`.`problemSet_id` IN %s \
                                                    AND ((`c2g_problem_sets`.`submissions_permitted` = 0  AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`) \
                                                    OR (`c2g_problem_sets`.`submissions_permitted` > 0  AND `c2g_problem_sets`.`submissions_permitted` >=  `c2g_problem_activity`.`attempt_number` \
                                                    AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`))) \
                                                    GROUP BY `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, \
                                                    `c2g_problem_sets`.`partial_credit_deadline`, `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName` \
                                                    ORDER BY NULL", [user.id, tuple(problem_set_list)])
                                else:
                                    cursor.execute("SELECT `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, `c2g_problem_sets`.`partial_credit_deadline`,  \
                                                   `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName`, \
                                                    count(`c2g_problem_activity`.`attempt_number`) AS `num_attempts`, \
                                                    MAX(`c2g_problem_activity`.`time_created`) AS `last_valid_attempt_time`, \
                                                    MAX(`c2g_problem_activity`.`complete`) AS `correct`, \
                                                    min(case when c2g_problem_activity.complete = 1 then c2g_problem_activity.id else null end) as `first_correct_answer`, \
                                                    max(c2g_problem_activity.id) as `max_activity_id` \
                                                    FROM `c2g_problem_activity` \
                                                    LEFT OUTER JOIN `c2g_problemset_to_exercise` ON (`c2g_problem_activity`.`problemset_to_exercise_id` = `c2g_problemset_to_exercise`.`id`) \
                                                    INNER JOIN `c2g_problem_sets` ON (`c2g_problemset_to_exercise`.`problemSet_id` = `c2g_problem_sets`.`id`) \
                                                    INNER JOIN `c2g_exercises` ON (`c2g_problemset_to_exercise`.`exercise_id` = `c2g_exercises`.`id`) \
                                                    WHERE (`c2g_problem_activity`.`student_id` = %s AND `c2g_problemset_to_exercise`.`problemSet_id` = %s \
                                                    AND ((`c2g_problem_sets`.`submissions_permitted` = 0  AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`) \
                                                    OR (`c2g_problem_sets`.`submissions_permitted` > 0  AND `c2g_problem_sets`.`submissions_permitted` >=  `c2g_problem_activity`.`attempt_number` \
                                                    AND `c2g_problem_sets`.`partial_credit_deadline` >  `c2g_problem_activity`.`time_created`))) \
                                                    GROUP BY `c2g_problemset_to_exercise`.`problemSet_id`, `c2g_problem_sets`.`submissions_permitted`, `c2g_problem_sets`.`resubmission_penalty`, \
                                                    `c2g_problem_sets`.`partial_credit_deadline`, `c2g_problem_sets`.`grace_period`, `c2g_problem_sets`.`late_penalty`, `c2g_exercises`.`fileName` \
                                                    ORDER BY NULL", [user.id, problem_set_list[0]])
                                
                                score_list = []
                                for row in cursor.fetchall():
                                    problemset_id = row[0]
                                    submissions_permitted = row[1]
                                    resubmission_penalty = row[2]
                                    partial_credit_deadline = row[3]
                                    grace_period = row[4]
                                    late_penalty = row[5]
                                    filename = row[6]
                                    num_attempts = row[7]
                                    last_valid_attempt_time = row[8]
                                    correct = row[9]
                                    first_correct_answer = row[10]
                                    max_activity_id = row[11]                                
                                
                                    score_item = {'problemset_id' : problemset_id,
                                                  'submissions_permitted' : submissions_permitted,
                                                  'resubmission_penalty' : resubmission_penalty,
                                                  'partial_credit_deadline' : partial_credit_deadline,
                                                  'grace_period' : grace_period,
                                                  'late_penalty' : late_penalty,
                                                  'filename' : filename,
                                                  'num_attempts' : num_attempts,
                                                  'last_valid_attempt_time' : last_valid_attempt_time,
                                                  'correct' : correct,
                                                  'first_correct_answer' : first_correct_answer,
                                                  'max_activity_id' : max_activity_id
                                                 }
                                    score_list.append(score_item)
                            
                                for section in sections:
                                    for problem_set in problem_sets:
                                        if problem_set.section_id == section.id:
                                            numQuestions = 0
                                            for psetToEx in psetToExs:
                                                if psetToEx['problemSet'] == problem_set.id:
                                                    numQuestions = psetToEx['dcount']
                                                    break
                            
                                            numCompleted = 0
                                            for pset_activity in pset_activities:
                                                if pset_activity['problemset_to_exercise__problemSet_id'] == problem_set.id and not filename_in_deleted_list(pset_activity['problemset_to_exercise__exercise__fileName'], problem_set.id, deleted_exercise_list):
                                                    if pset_activity['correct'] == 1:
                                                        numCompleted += 1
                                                    elif pset_activity['problemset_to_exercise__problemSet__submissions_permitted'] != 0 and pset_activity['num_attempts'] >= pset_activity['problemset_to_exercise__problemSet__submissions_permitted']:
                                                        numCompleted +=1
                            
                                            old_numCompleted = problem_set.get_progress(user)
                            
                                            if old_numCompleted != numCompleted:
                                                logfile.write("****FC : course_id : " + str(course.id) + " pset_id : " + str(problem_set.id) + " user_id : " + str(user.id) + " old : " + str(old_numCompleted) + " new : " + str(numCompleted) + "\n")
                                            else:
                                                logfile.write("**PC : course_id : " + str(course.id) + " pset_id : " + str(problem_set.id) + " user_id : " + str(user.id) + " old : " + str(old_numCompleted) + " new : " + str(numCompleted) + "\n")
                                                
                                            score = 0.0
                                            old_score = 0.0
                                            for score_item in score_list:
                                                problemset_id = score_item['problemset_id']
                                                submissions_permitted = score_item['submissions_permitted']
                                                resubmission_penalty = score_item['resubmission_penalty']
                                                partial_credit_deadline = score_item['partial_credit_deadline']
                                                grace_period = score_item['grace_period']
                                                late_penalty = score_item['late_penalty']
                                                filename = score_item['filename']
                                                num_attempts = score_item['num_attempts']
                                                last_valid_attempt_time = score_item['last_valid_attempt_time']
                                                correct = score_item['correct']
                                                first_correct_answer = score_item['first_correct_answer']
                                                max_activity_id = score_item['max_activity_id']
                                
                                                if problemset_id == problem_set.id and not filename_in_deleted_list(filename, problemset_id, deleted_exercise_list):
                                                    exercise_percent = 100
                                                    if first_correct_answer == None or first_correct_answer == max_activity_id:
                                                                                        
                                                        if correct == 0:
                                                            exercise_percent = 0
                                                        else:
                                                            exercise_percent -= resubmission_penalty*(num_attempts -1)

                                                            if last_valid_attempt_time > grace_period:
                                                                exercise_percent = int(exercise_percent*(100 - late_penalty)/100.0)
                            
                                                        #floor exercise percent at 0
                                                        exercise_percent = max(exercise_percent,0)
            
                                                        #add to total_score
                                                        score += exercise_percent/100.0
                            
                                                    else:
                                                        logfile.write("Bad data\n")
                                                        score = problem_set.get_score(user)
                                                        break
                            
                                            old_score = problem_set.get_score(user)
                                                
                                            if old_score != score:
                                                logfile.write("****FS : course_id : " + str(course.id) + " pset_id : " + str(problem_set.id) + " user_id : " + str(user.id) + " old : " + str(old_score) + " new : " + str(score) + "\n")
                                            else:
                                                logfile.write("**PS : course_id : " + str(course.id) + " pset_id : " + str(problem_set.id) + " user_id : " + str(user.id) + " old : " + str(old_score) + " new : " + str(score) + "\n")           
                                            
    logfile.close()
    
