from c2g.models import *
import json
from courses.reports.generation.C2GReportWriter import *

def gen_quiz_data_report(ready_course, ready_quiz, save_to_s3=False):
    students_ = ready_course.student_group.user_set.all().values_list('id', 'username', 'first_name', 'last_name')
    students = {}
    for s in students_: students[s[0]] = {"username": s[1], "name": "%s %s" % (s[2], s[3])}
    
    mean = lambda k: sum(k)/len(k)
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    is_video = isinstance(ready_quiz, Video)
    is_summative = (not is_video) and (ready_quiz.assessment_type == 'assessive')
    if is_summative:
        submissions_permitted = ready_quiz.submissions_permitted
        if submissions_permitted == 0: submissions_permitted = 100000
        resubmission_penalty = ready_quiz.resubmission_penalty/100.0
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, ready_quiz.slug)
    if is_video:
        s3_filepath = "%s/%s/reports/videos/%s" % (course_prefix, course_suffix, report_name)
    else:
        s3_filepath = "%s/%s/reports/problemsets/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    rw.write(["Activity for %s \"%s\" in %s (%s %d)" % ('Video' if is_video else 'Problem Set', ready_quiz.title, ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1) 

    data = {}
    
    if is_video: rlns = VideoToExercise.objects.filter(video=ready_quiz, is_deleted=0).order_by('video_time')
    else: rlns = ProblemSetToExercise.objects.filter(problemSet=ready_quiz, is_deleted=0).order_by('number')
    
    if is_video:
        video_visits = PageVisitLog.objects.filter(page_type='video', object_id = str(ready_quiz.id)).order_by('user', 'time_created')
        for vv in video_visits:
            if not vv.user.username in data:
                stud_username = vv.user.username
                stud_fullname = vv.user.first_name + " " + vv.user.last_name
                data[vv.user.username] = {'username': stud_username, 'name': stud_fullname, 'visits':[]}
            data[vv.user.username]['visits'].append("%s-%s-%s at %s:%s" % (vv.time_created.year, vv.time_created.month, vv.time_created.day, vv.time_created.hour, vv.time_created.minute))

    ex_ids = []
    for rln in rlns:
        ex = rln.exercise
        ex_ids.append(ex.id)
        
        if is_video:
            atts = ProblemActivity.objects.select_related('video', 'exercise').filter(video_to_exercise__exercise__fileName=ex.fileName, video_to_exercise__video=ready_quiz).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content')
        else:
            atts = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__exercise__fileName=ex.fileName, problemset_to_exercise__problemSet=ready_quiz).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content')
        
        submitters = [item[0] for item in atts]
        completes = [item[1] for item in atts]
        times_taken = [item[2] for item in atts]
        attempts_content = [item[3] for item in atts]
        
        for i in range(0, len(atts)):
            if not (submitters[i] in students): continue # Do not include attempts by non-students in the report
            
            is_student_first_attempt = (i == 0) or (submitters[i] != submitters[i-1])
            is_student_last_attempt = (i == len(atts)-1) or (submitters[i] != submitters[i+1])
            
            if is_student_first_attempt:
                stud_username = students[submitters[i]]['username']
                if not stud_username in data:
                    stud_fullname = students[submitters[i]]['name']
                    data[stud_username] = {'username': stud_username, 'name': stud_fullname, 'visits':[]}
                attempt_number = 0
                completed = False
                attempt_times = []
                attempts = []
                num_incorrect_attempts = 0
            
            attempt_number += 1
            
            if not completed:
                attempt_times.append(times_taken[i])
                attempts.append(attempts_content[i].replace("\r", "").replace("\n", ";"))
            
            if completes[i] == 1:
                completed = True
                num_incorrect_attempts = attempt_number - 1
            
            if is_student_last_attempt:
                score = 0
                if is_summative:
                    if completed and (num_incorrect_attempts+1 <= submissions_permitted):
                        score = 1 - (num_incorrect_attempts)*resubmission_penalty
                    if score < 0: score = 0
                
                data[stud_username][ex.id] = {'completed': 'y' if completed else 'n', 'attempts': json.dumps(attempts), 'median_attempt_time': median(attempt_times)}
                if is_summative: data[stud_username][ex.id]['score'] = score
                
    # Sort students by username
    sorted_usernames = sorted(data.keys())
    
    # If not activity, do not type anything unneeded.
    if len(sorted_usernames) == 0:
        rw.write(content=["No activity yet for this %s" % ('video' if is_video else 'problem set')], indent=1)
        report_content = rw.writeout()
        return {'name': report_name, 'path': s3_filepath, 'content': report_content}
        
    header1 = ["", ""]
    header2 = ["", ""]
    
    if is_video:
        header1.extend(["", "", "Num video visits", "Visits date/times"])
        header2.extend(["", "", "", ""])
        
    for rln in rlns:
        header1.extend(["", "", rln.exercise.get_slug(), "", "", ""])
        header2.extend(["", "", "Completed", "attempts"])
        if is_summative: header2.append("Score")
        header2.append("Median attempt time")
        
    if is_summative: header1.extend(["", "Total score / %d" % len(rlns)])
    rw.write(header1)
    rw.write(header2)
    
    for u in sorted_usernames:
        r = data[u]
        stud_score = 0
        content = [u, r['name']]
        if is_video:
            visit_dt_string = ""
            for vvi in range(len(data[u]['visits'])):
                if vvi > 0: visit_dt_string += ', '
                visit_dt_string += data[u]['visits'][vvi]
                
            content.extend(["", "", len(data[u]['visits']), visit_dt_string])
        
        for ex_id in ex_ids:
            if ex_id in r: ex_res = r[ex_id]
            else: ex_res = {'completed': '', 'attempts': '', 'score': '', 'median_attempt_time': ''}
            
            content.extend(["", "", ex_res['completed'], ex_res['attempts']])
            if is_summative:
                content.append(ex_res['score'])
                stud_score += (ex_res['score'] if isinstance(ex_res['score'], float) else 0)
            content.append(ex_res['median_attempt_time'])
        if is_summative: content.extend(["", stud_score])    
        rw.write(content)
        
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}
    
def median(l):
    if len(l) == 0: return None
    
    l = sorted(l)
    if (len(l)%2) == 0: return (l[len(l)/2] + l[(len(l)-1)/2]) / 2.0
    else:
        return l[(len(l)-1)/2]