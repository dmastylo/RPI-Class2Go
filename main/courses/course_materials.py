from c2g.models import *
import datetime
from django.db.models import Count, Max, Q, F
from django.db import connection, transaction



def get_course_materials(common_page_data, get_video_content=False, get_pset_content=False, get_additional_page_content = False, get_file_content=False):
    section_structures = []
    if common_page_data['request'].user.is_authenticated():
        sections = ContentSection.objects.getByCourse(course=common_page_data['course'])
        pages = AdditionalPage.objects.getSectionPagesByCourse(course=common_page_data['course'])
        files = File.objects.getByCourse(course=common_page_data['course'])
        groups = ContentGroup.objects.getByCourse(course=common_page_data['course'])
        level1_items, level2_items = group_data(groups)

        if get_video_content:
            videos = Video.objects.getByCourse(course=common_page_data['course'])
            if videos:
                video_list = []
                for video in videos:
                    video_list.append(video.id)
                videoToExs = VideoToExercise.objects.values('video').filter(video__in=video_list, is_deleted=0).annotate(dcount=Count('video'))
                    
                if common_page_data['course_mode'] == 'ready':
                    video_recs = VideoActivity.objects.filter(course=common_page_data['course'], student=common_page_data['request'].user)
                    video_downloads = VideoDownload.objects.values('video').filter(course=common_page_data['course'], student=common_page_data['request'].user).annotate(dcount=Count('video'))

        if get_pset_content:
            
            problem_sets = ProblemSet.objects.getByCourse(course=common_page_data['course'])
            if problem_sets:
                problem_set_list = []
                for problem_set in problem_sets:
                    problem_set_list.append(problem_set.id)
                psetToExs = ProblemSetToExercise.objects.values('problemSet').filter(problemSet__in=problem_set_list, is_deleted=0).annotate(dcount=Count('problemSet'))

                if common_page_data['course_mode'] == 'ready':
                    pset_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter(problemset_to_exercise__problemSet_id__in=problem_set_list, student=common_page_data['request'].user).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'))
                    
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
                    
                    key = 'page:' + str(page.id)
                    if page.section_id == section.id and not level2_items.has_key(key):
                        children = get_children(key, level1_items, level2_items)
                        
                        item = {'type':'additional_page', 'additional_page':page, 'index':page.index, 'children': children}

                        if common_page_data['course_mode'] == 'draft':
                            prod_page = page.image
                            if not prod_page.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_page.live_datetime > datetime.datetime.now():
                                    year = prod_page.live_datetime.year
                                    month = prod_page.live_datetime.month
                                    day = prod_page.live_datetime.day
                                    hour = prod_page.live_datetime.hour
                                    minute = prod_page.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"

                            item['visible_status'] = visible_status

                        section_dict['items'].append(item)

            if get_file_content:
                for file in files:
                    
                    key = 'file:' + str(file.id)
                    if file.section_id == section.id and not level2_items.has_key(key):
                        children = get_children(key, level1_items, level2_items)
                        
                        item = {'type':'file', 'file':file, 'index':file.index, 'children': children}

                        if common_page_data['course_mode'] == 'draft':
                            prod_file = file.image
                            if not prod_file.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_file.live_datetime > datetime.datetime.now():
                                    year = prod_file.live_datetime.year
                                    month = prod_file.live_datetime.month
                                    day = prod_file.live_datetime.day
                                    hour = prod_file.live_datetime.hour
                                    minute = prod_file.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"

                            item['visible_status'] = visible_status

                        section_dict['items'].append(item)

            if get_video_content:
                        
                for video in videos:
                    
                    key = 'video:' + str(video.id)
                    if video.section_id == section.id and not level2_items.has_key(key):
                        children = get_children(key, level1_items, level2_items)
                                
                        item = {'type':'video', 'video':video, 'completed_percent': 0, 'index':video.index, 'children': children}

                        numQuestions = 0
                        for videoToEx in videoToExs:
                            if videoToEx['video'] == video.id:
                                numQuestions = videoToEx['dcount']
                                break
                        
                        if common_page_data['course_mode'] == 'draft':
                            prod_video = video.image
                            if not prod_video.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_video.live_datetime > datetime.datetime.now():
                                    year = prod_video.live_datetime.year
                                    month = prod_video.live_datetime.month
                                    day = prod_video.live_datetime.day
                                    hour = prod_video.live_datetime.hour
                                    minute = prod_video.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"

                            item['visible_status'] = visible_status
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
                    key = 'pset:' + str(problem_set.id)
                    if problem_set.section_id == section.id and not level2_items.has_key(key):
                        children = get_children(key, level1_items, level2_items)
                        
                        item = {'type':'problem_set', 'problem_set':problem_set, 'index':problem_set.index, 'children': children}

                        numQuestions = 0
                        for psetToEx in psetToExs:
                            if psetToEx['problemSet'] == problem_set.id:
                                numQuestions = psetToEx['dcount']
                                break                            
                            
                        if common_page_data['course_mode'] == 'draft':
                            prod_problem_set = problem_set.image
                            if not prod_problem_set.live_datetime:
                                visible_status = "<span style='color:#A00000;'>Not Live</span>"
                            else:
                                if prod_problem_set.live_datetime > datetime.datetime.now():
                                    year = prod_problem_set.live_datetime.year
                                    month = prod_problem_set.live_datetime.month
                                    day = prod_problem_set.live_datetime.day
                                    hour = prod_problem_set.live_datetime.hour
                                    minute = prod_problem_set.live_datetime.minute
                                    visible_status = "<span style='color:#A07000;'>Live %02d-%02d-%04d at %02d:%02d</span>" % (month,day,year,hour,minute)
                                else:
                                    visible_status = "<span style='color:green;'>Live</span>"
                            item['visible_status'] = visible_status
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
                                        score = problem_set.get_score(common_page_data['request'].user)
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

            if common_page_data['course_mode'] == 'draft' or len(section_dict['items']) > 0:
                section_dict['items'] = sorted(section_dict['items'], key=lambda k: k['index'])
                section_structures.append(section_dict)
                index += 1

    return section_structures

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
    
def filename_in_deleted_list(filename, problem_set_id, deleted_exercise_list):
    for item in deleted_exercise_list:
        if item['filename'] == filename and item['problemset_id'] == problem_set_id:
            return True
            
    return False

def group_data(groups):
    
    level1_items = {}
    level2_items = {}
    
    group_id = None
    for group in groups:
        if group.group_id == group_id:
            level, type, id = get_group_item_data(group)
            if level == 2:
                level2_items[type + ':' + str(id)] = str(group_id)
        else:
            group_id = group.group_id
            level, type, id = get_group_item_data(group)
            if level == 1:
                level1_items[type + ':' + str(id)] = group_id
            
    return level1_items, level2_items
                
def get_group_item_data(group):
    if group.video_id:
        level = group.level
        type = 'video'
        id = group.video_id
    elif group.problemSet_id:
        level = group.level
        type = 'pset'
        id = group.problemSet_id
    elif group.additional_page_id:
        level = group.level
        type = 'page'
        id = group.additional_page_id
    elif group.file_id:
        level = group.level
        type = 'file'
        id = group.file_id
    elif group.exam_id:
        level = group.level
        type = 'exam'
        id = group.exam_id

    return level, type, id

def get_children(key, level1_items, level2_items):
    children = []
    if level1_items.has_key(key):
        group_id = level1_items[key]
        child_items = [k for k, v in level2_items.items() if str(group_id) in v]
        for child in child_items:
            child_item = {}
            type, url = get_child_data(child)
            child_item['type'] = type
            child_item['url'] = url
            children.append(child_item)
    return children
    
def get_child_data(child):
    parts = str(child).split(":")
    type = parts[0]
    id = parts[1]
    
    if type == 'video':
        video = Video.objects.get(id=id)
        url = 'videos/' + video.slug
    elif type == 'pset':
        pset = ProblemSet.objects.get(id=id)
        url = 'problemsets/' + pset.slug
    elif type == 'page':
        page = AdditionalPage.objects.get(id=id)
        url = 'pages/' + page.slug
    elif type == 'file':
        file = File.objects.get(id=id)
        url = file.file.url
    else:
        url = ''
    
    return type, url
