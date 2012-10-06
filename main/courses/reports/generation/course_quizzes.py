from c2g.models import *
from courses.reports.generation.C2GReportWriter import *
import math

def gen_course_quizzes_report(ready_course, save_to_s3=False):
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s-Course-Quizzes.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix)
    s3_filepath = "%s/%s/reports/course_quizzes/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    # Title
    rw.write(content = ["Course Quizzes for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    
    # Get a list of Quizzes (Problem sets and videos with exercises)
    quizzes = []
    problemsets = ProblemSet.objects.getByCourse(course=ready_course)
    for ps in problemsets:
        quizzes.append(ps)
        
    videos = Video.objects.getByCourse(course=ready_course)
    for vd in videos:
        quizzes.append(vd)
        
    quizzes = sorted(quizzes, key=lambda k:k.live_datetime, reverse=True)
    
    for q in quizzes:
        WriteQuizDataToReport(q, rw)

    report_content = rw.writeout()
    return {'name': "%02d_%02d_%02d__%02d_%02d_%02d-%s-Quizzes.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix), 'content': report_content, 'path': s3_filepath}
        
def WriteQuizDataToReport(q, rw):
    mean = lambda k: sum(k)/len(k)

    assessment_type = 'formative'
    
    if isinstance(q, Video): type = 'Video'
    else:
        if q.assessment_type == 'assessive':
            type = 'Summative problem set'
            assessment_type = 'summative'
            submissions_permitted = q.submissions_permitted
            if submissions_permitted == 0: submissions_permitted = 100000
            resubmission_penalty = q.resubmission_penalty / 100.0
        else: type = 'Formative problem set'
    
    rw.write(["%s (%s)" % (q.title, type)])
    
    # Get exercises
    if isinstance(q, Video):
        exercise_rlns = VideoToExercise.objects.filter(video=q, is_deleted=0).order_by('video_time')
        
    else:
        exercise_rlns = ProblemSetToExercise.objects.filter(problemSet=q, is_deleted=0).order_by('number')
        exercises = exercise_rlns.values_list('exercise', flat=True)
        
    if len(exercise_rlns) == 0:
        rw.write(content = ["No exercises have been added yet"], indent = 1, nl = 1)
        return
    
    q_scores = {}
    e_data_list = []
    
    
    for rln in exercise_rlns:
        ex = rln.exercise
        
        e_data = {
            'exercise':ex,
            'scores': [],
            'num_attempts': 0,
            'num_attempting_students':"",
            'num_attempts_per_student': "",
            'num_correct_attempts':"",
            'attempt_times': "",
            'num_correct_first_attempts':"",
            'num_correct_second_attempts':"",
            'num_correct_third_attempts':"",
        }
        
        if isinstance(q, Video):
            atts = ProblemActivity.objects.select_related('video', 'exercise').filter(video_to_exercise__exercise__fileName=ex.fileName, video_to_exercise__video=q).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content')
        else:
            atts = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__exercise__fileName=ex.fileName, problemset_to_exercise__problemSet=q).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content')
        
        submitters = [item[0] for item in atts]
        completes = [item[1] for item in atts]
        attempt_times = [item[2] for item in atts]
        attempts_content = [item[3] for item in atts]
        
        stud_index = -1
        unique_submitters = []
        unique_submitters_num_attempts = []
        unique_submitters_correct_attempt_number = []
        unique_submitters_scores = []
        
        if len(submitters) > 0:
            for i in range(0, len(submitters)):
                is_first_student_attempt = (i == 0) or submitters[i] != submitters[i-1]
                is_last_student_attempt = (i == len(submitters)-1) or submitters[i] != submitters[i+1]
                
                if is_first_student_attempt:
                    stud_index += 1
                    unique_submitters.append(submitters[i])
                    unique_submitters_num_attempts.append(0)
                    unique_submitters_correct_attempt_number.append(-1)
                    unique_submitters_scores.append(0)
                    first_attempt_index = i
                
                unique_submitters_num_attempts[stud_index] += 1
                attempt_number = i - first_attempt_index
                
                if completes[i] == 1:
                    unique_submitters_correct_attempt_number[stud_index] = attempt_number + 1
                    if assessment_type == 'summative':
                        if (attempt_number+1) > submissions_permitted: unique_submitters_scores[stud_index] = 0
                        else:
                            unique_submitters_scores[stud_index] = 1 - attempt_number * (resubmission_penalty)
                            if unique_submitters_scores[stud_index] < 0: unique_submitters_scores[stud_index] = 0
                        
                if is_last_student_attempt and assessment_type == 'summative': # Before leaving to the next student, register the student score if the quiz is a summ. ps.
                    if submitters[i] in q_scores: q_scores[submitters[i]] += unique_submitters_scores[stud_index]
                    else: q_scores[submitters[i]] = 0
        
            e_data = {
                'exercise':ex,
                'scores': unique_submitters_scores,
                'num_attempts': len(submitters),
                'num_attempting_students':len(unique_submitters),
                'num_attempts_per_student': 1.0*len(submitters)/len(unique_submitters),
                'num_correct_attempts':completes.count(1),
                'attempt_times': attempt_times,
                'num_correct_first_attempts':unique_submitters_correct_attempt_number.count(1),
                'num_correct_second_attempts':unique_submitters_correct_attempt_number.count(2),
                'num_correct_third_attempts':unique_submitters_correct_attempt_number.count(3),
            }
            
            e_data_list.append(e_data)
        
    if assessment_type == 'summative':
        q_scores_values = q_scores.values()
        if len(q_scores_values) > 0: rw.write(["Mean score", mean(q_scores_values), "Max score", max(q_scores_values)], indent = 1, nl = 1)
    
    content = ["Exercise"]
    if assessment_type == 'summative': content.extend(["Mean score", "Max score"])
    content.extend(["Total attempts", "Students who have attempted", "Avg. attempts per student", "Correct attempts", "Correct 1st attempts", "Correct 2nd attempts", "Correct 3rd attempts", "Median attempt time"])
    rw.write(content, indent = 1)
    
    for e_data in e_data_list:
        content = [e_data['exercise'].get_slug()]
        if assessment_type == 'summative': content.extend([mean(e_data['scores']), max(e_data['scores'])])
        content.extend([e_data['num_attempts'], e_data['num_attempting_students'], e_data['num_attempts_per_student'], e_data['num_correct_attempts'], e_data['num_correct_first_attempts'], e_data['num_correct_second_attempts'], e_data['num_correct_third_attempts'], median(e_data['attempt_times']) if len(e_data['attempt_times']) > 0 else ""])
        rw.write(content, indent = 1)
        
    rw.write([""])    

def median(l):
    if len(l) == 0: return None
    
    l = sorted(l)
    if (len(l)%2) == 0: return (l[len(l)/2] + l[(len(l)-1)/2]) / 2.0
    else: return l[(len(l)-1)/2]