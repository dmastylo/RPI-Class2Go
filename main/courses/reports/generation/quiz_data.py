from c2g.models import *
import json
# import csv
# from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
# from django.core.files.storage import default_storage
# from storages.backends.s3boto import S3BotoStorage
from courses.reports.generation.C2GReportWriter import *

def gen_quiz_data_report(ready_course, ready_quiz, save_to_s3=False):
    
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    s3_filepath = "%s/%s/reports/quiz_data/%s/%02d_%02d_%02d__%02d_%02d_%02d-%s-Quiz-Data.csv" % (course_prefix, course_suffix, ready_quiz.slug, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, ready_quiz.slug)
    
    rw = C2GReportWriter(ready_course, save_to_s3, s3_filepath)
    rw.write(["Quiz Attempts for Quiz \"%s\" in %s (%s %d)" % (ready_quiz.title, ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1) 
    
    is_summative = isinstance(ready_quiz, ProblemSet) and (ready_quiz.assessment_type == 'summative')
    
    data = {}
    mean = lambda k: sum(k)/len(k)
    
    if isinstance(ready_quiz, Video): rlns = VideoToExercise.objects.get(video=ready_quiz).order_by('video_time')
    else: rlns = ProblemSetToExercise.objects.filter(problemSet=ready_quiz,).order_by('number')
    
    ex_ids = []
    for rln in rlns:
        ex = rln.exercise
        ex_ids.append(ex.id)
        
        if isinstance(ready_quiz, Video): atts = ProblemActivity.objects.filter(video_to_exercise = rln).order_by('student', 'time_created')
        else: atts = ProblemActivity.objects.filter(problemset_to_exercise = rln).order_by('student', 'time_created')
        
        submitters = atts.values_list('student', flat=True)
        completes = atts.values_list('complete', flat=True)
        times_taken = atts.values_list('time_taken', flat=True)
        attempts_content = atts.values_list('attempt_content', flat=True)
        
        
        for i in range(0, len(atts)):
            is_student_first_attempt = (i == 0) or (submitters[i] != submitters[i-1])
            is_student_last_attempt = (i == len(atts)-1) or (submitters[i] != submitters[i+1])
            
            if is_student_first_attempt:
                attempt_number = 0
                stud_username = atts[i].student.username
                stud_fullname = atts[i].student.first_name + " " + atts[i].student.last_name
                completed = False
                attempt_times = []
                attempts = []
            
            attempt_number += 1
            
            if not completed:
                attempt_times.append(times_taken[i])
                attempts.append(attempts_content[i])
            
            if completes[i] == 1: completed = True
            
            if is_student_last_attempt:
                score = 0
                if is_summative:
                    if (attempt_number + 1) <= ready_quiz.submissions_permitted:
                        score = 1 - attempt_number*ready_quiz.resubmission_penalty/100.0
                    if score < 0: score = 0
                
                if not stud_username in data: data[stud_username] = {'username': stud_username, 'name': stud_fullname}
                
                data[stud_username][ex.id] = {'completed': 'y' if completed else 'n', 'attempts': json.dumps(attempts), 'mean_attempt_time': mean(attempt_times)}
                if is_summative: data[stud_username][ex.id]['score'] = score
    
    # Sort students by username
    sorted_usernames = sorted(data.keys())
    
    header1 = ["", ""]
    header2 = ["", ""]
    for rln in rlns:
        header1.extend(["", "", rln.exercise.get_slug(), "", "", ""])
        header2.extend(["", "", "Completed", "attemps"])
        if is_summative: header2.append("Score")
        header2.append("Mean attempt time")
        
    if is_summative: header1.extend(["", "Total score / %d" % len(rlns)])
    rw.write(header1)
    rw.write(header2)
    
    for u in sorted_usernames:
        r = data[u]
        stud_score = 0
        content = [u, r['name']]
        for ex_id in ex_ids:
            if ex_id in r: ex_res = r[ex_id]
            else: ex_res = {'completed': '', 'attempts': '', 'score': '', 'mean_attempt_time': ''}
            
            content.extend(["", "", ex_res['completed'], ex_res['attempts']])
            if is_summative:
                content.append(ex_res['score'])
                stud_score += (ex_res['score'] if isinstance(ex_res['score'], float) else 0)
            content.append(ex_res['mean_attempt_time'])
        if is_summative: content.extend(["", stud_score])    
        rw.write(content)
        
    rw.close()
     