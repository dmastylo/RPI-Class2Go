from c2g.models import *
import datetime
from django.db.models import Count, Max, Q, F


def get_course_materials(common_page_data, get_video_content=False, get_pset_content=False, get_additional_page_content = False, get_file_content=False):
    section_structures = []
    if common_page_data['request'].user.is_authenticated():
        sections = ContentSection.objects.getByCourse(course=common_page_data['course'])
        pages = AdditionalPage.objects.getSectionPagesByCourse(course=common_page_data['course'])
        files = File.objects.getByCourse(course=common_page_data['course'])

        if get_video_content:
            videos = Video.objects.getByCourse(course=common_page_data['course'])
            if videos:
                video_list = []
                for video in videos:
                    video_list.append(video.id)
                videoToExs = VideoToExercise.objects.values('video').filter(video__in=video_list, is_deleted=0).annotate(dcount=Count('video'))
                    
                if common_page_data['course_mode'] == 'ready':
                    video_recs = VideoActivity.objects.filter(course=common_page_data['course'], student=common_page_data['request'].user)

        if get_pset_content:
            
            problem_sets = ProblemSet.objects.getByCourse(course=common_page_data['course'])
            if problem_sets:
                problem_set_list = []
                for problem_set in problem_sets:
                    problem_set_list.append(problem_set.id)
                psetToExs = ProblemSetToExercise.objects.values('problemSet').filter(problemSet__in=problem_set_list, is_deleted=0).annotate(dcount=Count('problemSet'))

                if common_page_data['course_mode'] == 'ready':
                    pset_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter(problemset_to_exercise__problemSet_id__in=problem_set_list, student=common_page_data['request'].user).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'))
                    pset_score_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__problemSet__resubmission_penalty', 'problemset_to_exercise__problemSet__partial_credit_deadline', 'problemset_to_exercise__problemSet__grace_period', 'problemset_to_exercise__problemSet__late_penalty', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter( Q(problemset_to_exercise__problemSet_id__in=problem_set_list), Q(student=common_page_data['request'].user), (Q(problemset_to_exercise__problemSet__submissions_permitted=0) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created'))) | (Q(problemset_to_exercise__problemSet__submissions_permitted__gt=0) & Q(problemset_to_exercise__problemSet__submissions_permitted__gte=F('attempt_number')) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created')))).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'), last_valid_attempt_time=Max('time_created'))

        index = 0
        for section in sections:
            section_dict = {'section':section, 'items':[]}

            if get_additional_page_content:
                for page in pages:
                    if page.section_id == section.id:
                        item = {'type':'additional_page', 'additional_page':page, 'index':page.index}

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
                    if file.section_id == section.id:
                        item = {'type':'file', 'file':file, 'index':file.index}

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
                    if video.section_id == section.id:
                
                        item = {'type':'video', 'video':video, 'completed_percent': 0, 'index':video.index}

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
                            for video_rec in video_recs:
                                if video_rec.video_id == video.id:
                                    item['video_rec'] = video_rec
                                    if video.duration:
                                        item['completed_percent'] = 100.0 * video_rec.start_seconds / video.duration
                                    else:
                                        item['completed_percent'] = 0

                        item['numQuestions'] = numQuestions
                        section_dict['items'].append(item)

            if get_pset_content:

                for problem_set in problem_sets:
                    if problem_set.section_id == section.id:
                        item = {'type':'problem_set', 'problem_set':problem_set, 'index':problem_set.index}

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
                                if pset_activity['problemset_to_exercise__problemSet_id'] == problem_set.id:
                                    if pset_activity['correct'] == 1:
                                        numCompleted += 1
                                    elif pset_activity['problemset_to_exercise__problemSet__submissions_permitted'] != 0 and pset_activity['num_attempts'] >= pset_activity['problemset_to_exercise__problemSet__submissions_permitted']:
                                        numCompleted +=1
                                        
                            
                            score = 0.0
                            for pset_score_activity in pset_score_activities:
                                if pset_score_activity['problemset_to_exercise__problemSet_id'] == problem_set.id:
                                    exercise_percent = 100                                
                                    if pset_score_activity['correct'] == 0:
                                        exercise_percent = 0
                                    else:
                                        exercise_percent -= pset_score_activity['problemset_to_exercise__problemSet__resubmission_penalty']*(pset_score_activity['num_attempts'] -1)

                                        if pset_score_activity['last_valid_attempt_time'] > pset_score_activity['problemset_to_exercise__problemSet__grace_period']:
                                            exercise_percent = int(exercise_percent*(100 - pset_score_activity['problemset_to_exercise__problemSet__late_penalty'])/100.0)
                            
                                    #floor exercise percent at 0
                                    exercise_percent = max(exercise_percent,0)
            
                                    #add to total_score
                                    score += exercise_percent/100.0
                            
                            old_score = problem_set.get_score(common_page_data['request'].user)

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
    
    logfile = open('yyyy.log', 'w')
    
    #Get all courses
    courses = Course.objects.filter(mode='ready', id__gt=4)
    
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

                    for user in users:
                        user_groups = user.groups.all()
                        for g in user_groups:
                            if g.id == course.student_group_id:
                                
                                pset_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter(problemset_to_exercise__problemSet_id__in=problem_set_list, student=user).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'))
                                pset_score_activities = ProblemActivity.objects.values('problemset_to_exercise__problemSet_id', 'problemset_to_exercise__problemSet__submissions_permitted', 'problemset_to_exercise__problemSet__resubmission_penalty', 'problemset_to_exercise__problemSet__partial_credit_deadline', 'problemset_to_exercise__problemSet__grace_period', 'problemset_to_exercise__problemSet__late_penalty', 'problemset_to_exercise__exercise__fileName').select_related('problemset_to_exercise').filter( Q(problemset_to_exercise__problemSet_id__in=problem_set_list), Q(student=user), (Q(problemset_to_exercise__problemSet__submissions_permitted=0) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created'))) | (Q(problemset_to_exercise__problemSet__submissions_permitted__gt=0) & Q(problemset_to_exercise__problemSet__submissions_permitted__gte=F('attempt_number')) & Q(problemset_to_exercise__problemSet__partial_credit_deadline__gt=F('time_created')))).annotate(correct=Max('complete'), num_attempts=Max('attempt_number'), last_valid_attempt_time=Max('time_created'))
                                
                            
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
                                                if pset_activity['problemset_to_exercise__problemSet_id'] == problem_set.id:
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
                                            for pset_score_activity in pset_score_activities:
                                                
                                                if pset_score_activity['problemset_to_exercise__problemSet_id'] == problem_set.id:
                                                    exercise_percent = 100                        
                                                    if pset_score_activity['correct'] == 0:
                                                        exercise_percent = 0
                                                    else:
                                                        exercise_percent -= pset_score_activity['problemset_to_exercise__problemSet__resubmission_penalty']*(pset_score_activity['num_attempts'] - 1)
                                                        if pset_score_activity['last_valid_attempt_time'] > pset_score_activity['problemset_to_exercise__problemSet__grace_period']:
                                                            exercise_percent = int(exercise_percent*(100 - pset_score_activity['problemset_to_exercise__problemSet__late_penalty'])/100.0)
                            
                                                    #floor exercise percent at 0
                                                    exercise_percent = max(exercise_percent,0)
            
                                                    #add to total_score
                                                    score += exercise_percent/100.0
                            
                                            old_score = problem_set.get_score(user)
                                                
                                            if old_score != score:
                                                logfile.write("****FS : course_id : " + str(course.id) + " pset_id : " + str(problem_set.id) + " user_id : " + str(user.id) + " old : " + str(old_score) + " new : " + str(score) + "\n")
                                            else:
                                                logfile.write("**PS : course_id : " + str(course.id) + " pset_id : " + str(problem_set.id) + " user_id : " + str(user.id) + " old : " + str(old_score) + " new : " + str(score) + "\n")
                                                                                                
                                                
                                            
    logfile.close()    