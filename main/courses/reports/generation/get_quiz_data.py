from c2g.models import *
from operator import itemgetter
import json
import re
from django.db.models import Count, Avg, Q
from datetime import datetime

mean = lambda k: sum(k)/len(k)

def sanitize_string(s):
    return s.replace("\r", "").replace("\n", ";")

def get_quiz_data(ready_quiz, get_visits = False):
    # get_quiz_data: Returns a dict of dicts with quiz and quiz exercise information and per-student quiz data
    # The format of the output will be as follows. Every item in the outer dict has a key equal to a student username, and its value is an inner dict with the following kv_pairs:
    #   quiz:
    #       title (and type)
    #       assessment_type
    #       due date
    #       resubmission penalty (for summative psets only)
    #       submissions permitted (for summative psets only)
    #       grace period (for summative psets only)
    #       partial_credit_deadline (for summative psets only)
    #       late penalty (for summative psets only)
    #       scores
    #       scores_after_late_penalty
    #       total num students with at least one attempt
    #       total num students with attempts
    #
    #   exercises: A dict with one dict per exercise_id detailing the following:
    #       slug
    #       num_attempts (total)
    #       num_attempting_students
    #       num_correct_attempts
    #       num_correct_first_attempts
    #       num_correct_second_attempts
    #       num_correct_third_attempts
    #       median number of attempts
    #       median number of attempts upto and including first correct attempt
    #       median_attempt_time
    #       scores
    #       scores_with_late_penalty
    #       most_frequent_incorrect_answers (if at least one answer exceeds 5% of the total)
    #       
    #   per_student:
    #       username: Student username
    #       name: Student full name
    #       visits (if get_visits is true): will be a list of the dates/times at which the student visited the quiz
    #       exercise_activity: A dict where the keys are exercise IDs, and the values are dictionaries with the following k-v pairs:
    #           completed: 'y' if the student has completed the exercise, and 'n' otherwise
    #           attempts: a list of attempts _up_to_the_first_correct_attempt_.
    #           median_attempt_time
    #           last_attempt_timestamp
    #           score: The score of the student for the exercise
    #           score_after_late_penalty: for summative problem sets, this is the score adjusted by late penalties
    #       quiz_score: The total score of the student in the quiz
    #       quiz_score_after_late_penalty: Same as above, with late penalty applied (for summative psets)
    #       has_attempts: true if the student has at least one attempt for the quiz
    
    per_student_data = {}
    
    ### 1- Pre-populate per_student_data with a list of all students and empty fields
    students = ready_quiz.course.student_group.user_set.order_by('username').all().values_list('id', 'username', 'first_name', 'last_name')
    course_students = {}
    for s in students:
        s = (s[0], sanitize_string(s[1]), sanitize_string(s[2]), sanitize_string(s[3]))
        course_students[s[0]] = s[1]
        per_student_data[s[1]] = {
            'name': s[2] + " " + s[3],
            'visits':[],
            'exercise_activity': {},
            'quiz_score': 0,
            'quiz_score_after_late_penalty': 0,
            'has_attempts': False,
        }
    
    
    ### 2- Gather required information about the quiz object
    is_video = False
    is_summative = False
    is_formative = False
    is_survey = False
    
    if isinstance(ready_quiz, Video):
        is_video = True
        type="Video"
        assessment_type = "formative"
    else:
        if ready_quiz.assessment_type == 'assessive':
            is_summative = True
            type = "Summative Problem Set"
            assessment_type = "summative"
        elif ready_quiz.assessment_type == 'formative':
            is_formative = True
            type = "Formative Problem Set"
            assessment_type = "formative"
        else:
            is_survey = True
            type = "Survey"
            assessment_type = "survey"
    
    if is_summative:
        submissions_permitted = ready_quiz.submissions_permitted
        if submissions_permitted == 0: submissions_permitted = 100000
        resubmission_penalty = ready_quiz.resubmission_penalty/100.0
        grace_deadline = ready_quiz.grace_period
        if not grace_deadline: grace_deadline = ready_quiz.due_date
        partial_credit_deadline = ready_quiz.partial_credit_deadline
        late_penalty = ready_quiz.late_penalty / 100.0
    
    ### 3- Get visit data
    if get_visits:
        page_type = ('video' if is_video else 'problemset')
        visits = PageVisitLog.objects.filter(page_type = page_type, object_id = str(ready_quiz.id)).order_by('user', 'time_created')
        
        for visit in visits:
            username = visit.user.username
            if not username in per_student_data: continue # Visit is by a non course-student
            per_student_data[username]['visits'].append(format_datetime(visit.time_created))
    
    ### 4- Get all relationships to exercises
    if is_video:
        rlns = VideoToExercise.objects.filter(video=ready_quiz, is_deleted=0).order_by('video_time')
    else:
        rlns = ProblemSetToExercise.objects.filter(problemSet=ready_quiz, is_deleted=0).order_by('number')

    ### 5- Get student exercise activity for each student and each exercise
    exercises = []
    exs_median_attempt_times = {}
    exs_most_frequent_incorrect_answers = {}
    exs_nums_attempts = {}
    exs_nums_attempts_to_fca = {}
    exs_scores = {}
    exs_scores_after_late_penalty = {}
    
    for rln in rlns:
        ex = rln.exercise
        exercises.append(ex)
        
        if is_video:
            ex_atts = ProblemActivity.objects.select_related('video', 'exercise').filter(video_to_exercise__exercise__fileName=ex.fileName, video_to_exercise__video=ready_quiz).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content', 'time_created')
        else:
            ex_atts = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__exercise__fileName=ex.fileName, problemset_to_exercise__problemSet=ready_quiz).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content', 'time_created')
        
        num_ex_atts = len(ex_atts)
        
        ex_submitters = [item[0] for item in ex_atts]
        ex_completes = [item[1] for item in ex_atts]
        ex_times_taken = [item[2] for item in ex_atts]
        ex_attempts_content = [item[3] for item in ex_atts]
        ex_times_created = [item[4] for item in ex_atts]
        
        for i in range(len(ex_attempts_content)):
            ex_attempts_content[i] = sanitize_string(ex_attempts_content[i])
        
        exs_nums_attempts[ex.id] = [] # We will not count any attempts after a student's first correct one
        exs_nums_attempts_to_fca[ex.id] = []
        exs_median_attempt_times[ex.id] = median(ex_times_taken)
        exs_most_frequent_incorrect_answers[ex.id] = get_most_freq_inc_attempts(ex_attempts_content, ex_completes)
        exs_scores[ex.id] = []
        exs_scores_after_late_penalty[ex.id] = []
        
        for i in range(num_ex_atts):
            if not (ex_submitters[i] in course_students): continue # Do not include attempts by non course-students in the report
            
            is_student_first_attempt = (i == 0) or (ex_submitters[i] != ex_submitters[i-1])
            if is_student_first_attempt:
                stud_username = course_students[ex_submitters[i]]
                
                stud_attempt_number = 0
                stud_is_completed = False
                stud_attempts = []
                stud_attempt_times = []
                stud_score = 0
                stud_score_after_late_penalty = 0
            
            if stud_is_completed:
                continue # Skip all attempts after a first correct attempt has been found for the student
            
            stud_attempt_number += 1
            stud_attempt_times.append(ex_times_taken[i])
            stud_attempts.append(ex_attempts_content[i])
            
            if ex_completes[i] == 1:
                stud_is_completed = True

                if is_summative:
                    (stud_score, stud_score_after_late_penalty) = compute_score_summative(stud_attempt_number, ex_times_created[i], resubmission_penalty, submissions_permitted, grace_deadline, partial_credit_deadline, late_penalty)
                if is_formative or is_video:
                    stud_score = 1.0
                    stud_score_after_late_penalty = 1.0

            is_student_last_attempt = (i == num_ex_atts-1) or (ex_submitters[i] != ex_submitters[i+1])
            if stud_is_completed or is_student_last_attempt:
                per_student_data[stud_username]['exercise_activity'][ex.id] = {
                    'completed': stud_is_completed,
                    'attempts': json.dumps(stud_attempts),
                    'median_attempt_time': median(stud_attempt_times),
                    'last_attempt_timestamp': ex_times_created[i],
                    'score': stud_score,
                    'score_after_late_penalty': stud_score_after_late_penalty,
                }
                
                per_student_data[stud_username]['quiz_score'] += stud_score
                per_student_data[stud_username]['quiz_score_after_late_penalty'] += stud_score_after_late_penalty
                per_student_data[stud_username]['has_attempts'] = True
                
                exs_nums_attempts[ex.id].append(stud_attempt_number)
                if stud_is_completed: exs_nums_attempts_to_fca[ex.id].append(stud_attempt_number)
                exs_scores[ex.id].append(stud_score)
                exs_scores_after_late_penalty[ex.id].append(stud_score_after_late_penalty)

            # End of loop on exercise attempts
    
        # End of loop on quiz exercises
        
    ### 6- Get quiz stats
    quiz_scores = [per_student_data[username]['quiz_score'] for username in per_student_data]
    quiz_scores_after_late_penalty = [per_student_data[username]['quiz_score_after_late_penalty'] for username in per_student_data]
    num_students_with_attempts = 0
    for username in per_student_data:
        if per_student_data[username]['has_attempts']:
            num_students_with_attempts += 1
    
    quiz_summary = {
        'title': "%s (%s)" % (ready_quiz.title, type),
        'assessment_type': assessment_type,
        'scores': quiz_scores,
        'scores_after_late_penalty': quiz_scores_after_late_penalty,
        'total_num_students_with_attempts': num_students_with_attempts,
    }
    if is_summative:
        quiz_summary['due_date'] = format_datetime(ready_quiz.due_date)
        quiz_summary['resubmission_penalty'] = ready_quiz.resubmission_penalty
        quiz_summary['submissions_permitted'] = ready_quiz.submissions_permitted
        quiz_summary['grace_period'] = format_datetime(ready_quiz.grace_period)
        quiz_summary['partial_credit_deadline'] = format_datetime(ready_quiz.partial_credit_deadline)
        quiz_summary['late_penalty'] = ready_quiz.late_penalty
    
    ### 7- Get exercise stats
    exercise_summaries = []
    for ex in exercises:
        exercise_summaries.append({
            'id': ex.id,
            'slug': ex.get_slug(),
            'num_attempts': sum(exs_nums_attempts[ex.id]),
            'num_attempting_students': len(exs_nums_attempts[ex.id]),
            'median_num_attempts': median(exs_nums_attempts[ex.id]),
            'num_correct_attempts': len(exs_nums_attempts_to_fca[ex.id]),
            'median_num_attempts_to_fca': median(exs_nums_attempts_to_fca[ex.id]),
            'num_correct_first_attempts': exs_nums_attempts_to_fca[ex.id].count(1),
            'num_correct_second_attempts': exs_nums_attempts_to_fca[ex.id].count(2),
            'num_correct_third_attempts': exs_nums_attempts_to_fca[ex.id].count(3),
            'median_attempt_time': exs_median_attempt_times[ex.id],
            'scores': exs_scores[ex.id],
            'scores_after_late_penalty': exs_scores_after_late_penalty[ex.id],
            'most_frequent_incorrect_answers': exs_most_frequent_incorrect_answers[ex.id],
        })
        
    return {'quiz_summary': quiz_summary, 'exercise_summaries': exercise_summaries, 'per_student_data': per_student_data}
    

def get_assessment_data(ready_exam, get_visits = False):
    # get_assessment_data: Returns a dict of dicts with assessment data
    # The format of the output will be as follows. 
    # exam_summary contains for each field:
    #     total_attempts{human_name, # total attempts}
    #     distinct_students{human_name, # distinct students}
    #     mean_score{human_name, mean score}
    #     max_score{human_name, max score}
    #     correct_attempts{human_name, # correct attempts}
    #     correct_first_attempts{human_name, # correct first attempts}
    #     correct_second_attempts{human_name, # correct second attempts}
    #     correct_third_attempts{human_name, # correct third attempts}
    
    total_attempts = {}
    human_field = {}
    distinct_students = {}
    mean_score = {}
    max_score = {}
    correct_attempts = {}
    correct_first_attempts = {}
    correct_second_attempts = {}
    correct_third_attempts = {}
    
    #Get total_attempts and unique students
    field_attempts = ExamRecordScoreField.objects.values('human_name', 'field_name').select_related('parent').filter(parent__record__exam_id=ready_exam.id).annotate(total_attempts=Count('parent__record__attempt_number'), unique_students=Count('parent__record__student', distinct=True), mean_score=Avg('subscore'), max_score=Max('subscore'))
    for field_attempt in field_attempts:
        total_attempts[field_attempt['field_name']] = field_attempt['total_attempts']
        human_field[field_attempt['field_name']] = field_attempt['human_name']
        distinct_students[field_attempt['field_name']] = field_attempt['unique_students']
        mean_score[field_attempt['field_name']] = field_attempt['mean_score']
        max_score[field_attempt['field_name']] = field_attempt['max_score']
    
    #Get correct attempts
    field_correct_attempts = ExamRecordScoreField.objects.values('human_name', 'field_name').select_related('parent').filter(parent__record__exam_id=ready_exam.id, correct=1).annotate(correct_attempts=Count('correct'))
    for field_correct_attempt in field_correct_attempts:
        correct_attempts[field_correct_attempt['field_name']] = field_correct_attempt['correct_attempts']
    
    #Get correct first attempts
    field_correct_first_attempts = ExamRecordScoreField.objects.values('human_name', 'field_name').select_related('parent').filter(parent__record__exam_id=ready_exam.id, correct=1, parent__record__attempt_number=1).annotate(correct_first_attempts=Count('correct'))
    for field_correct_first_attempt in field_correct_first_attempts:
        correct_first_attempts[field_correct_first_attempt['field_name']] = field_correct_first_attempt['correct_first_attempts']
    
    #Get correct second attempts
    field_correct_second_attempts = ExamRecordScoreField.objects.values('human_name', 'field_name').select_related('parent').filter(parent__record__exam_id=ready_exam.id, correct=1, parent__record__attempt_number=2).annotate(correct_second_attempts=Count('correct'))
    for field_correct_second_attempt in field_correct_second_attempts:
        correct_second_attempts[field_correct_second_attempt['field_name']] = field_correct_second_attempt['correct_second_attempts']
    
    #Get correct third attempts
    field_correct_third_attempts = ExamRecordScoreField.objects.values('human_name', 'field_name').select_related('parent').filter(parent__record__exam_id=ready_exam.id, correct=1, parent__record__attempt_number=3).annotate(correct_third_attempts=Count('correct'))
    for field_correct_third_attempt in field_correct_third_attempts:
        correct_third_attempts[field_correct_third_attempt['field_name']] = field_correct_third_attempt['correct_third_attempts']
    
    exam_summary = {}
    exam_summary['title'] = ready_exam.title
    exam_summary['assessment_type'] = ready_exam.assessment_type
    exam_summary['total_attempts'] = total_attempts
    exam_summary['human_field'] = human_field
    exam_summary['distinct_students'] = distinct_students
    exam_summary['mean_score'] = mean_score
    exam_summary['max_score'] = max_score
    exam_summary['correct_attempts'] = correct_attempts
    exam_summary['correct_first_attempts'] = correct_first_attempts
    exam_summary['correct_second_attempts'] = correct_second_attempts
    exam_summary['correct_third_attempts'] = correct_third_attempts
    
    return exam_summary

def get_full_assessment_data(ready_exam, get_visits = False):

    #Get total score for each student that has attempted the exam
    student_scores = ExamScore.objects.values('student__username', 'student__first_name', 'student__last_name', 'score').select_related('student').filter(exam_id=ready_exam.id).order_by('student__username')

    #Get data for each field attempted
    student_field_scores = ExamRecordScoreField.objects.values('human_name', 'field_name', 'parent__record__student__username', 'parent__record__student__first_name', 'parent__record__student__last_name').select_related('parent').filter(parent__record__exam_id=ready_exam.id).annotate(correct=Max('correct'), sub_score=Max('subscore'), total_attempts=Count('parent__record__attempt_number')).order_by('parent__record__student__username')
    
    return student_scores, student_field_scores
    
def get_survey_data(ready_survey, get_visits = False):
    
    errors = 0
    
    #List of responses, with count, for each question
    tally = {}
    
    #Report friendly questions
    question_reports = {}
    
    #Get all the submissions for this survey
    exam_records = ExamRecord.objects.filter(exam=ready_survey)
    
    for exam_record in exam_records:
        json_row = exam_record.json_data
        
        try:
            data = json.loads(json_row)
            
        except ValueError:
            errors +=1
            
        else:
            for question in data.keys():
                answer = None
                question_report = None
                
                if type(data[question]) is dict and data[question].get('value', False):
                    #Single answer
                    
                    answer = data[question].get('value')
                    
                    if data[question].get('report', False):
                        question_report =  data[question].get('report')   
                    elif data[question].get('questionreport', False):
                        question_report =  str(question) + " : " + data[question].get('questionreport')
                    else:    
                        question_report = question
                        
                    question_reports[question] = question_report
                    tally = store_answer(tally, question, answer)
            
                else:
                    #Multiple answers
                    
                    list_of_dicts = data[question]    
                    for multi_answer_dict in list_of_dicts:                      
                        
                        if type(multi_answer_dict) is dict and multi_answer_dict.get('value', False):
                            
                            if multi_answer_dict.get('report', False):
                                answer = multi_answer_dict.get('report')
                            else:
                                answer = multi_answer_dict.get('value')
                                
                        if multi_answer_dict.get('questionreport', False):
                            question_report = multi_answer_dict.get('questionreport')
                        else:
                            question_report = question 
                        
                        question_reports[question] = question_report
                        tally = store_answer(tally, question, answer)
    
    return tally, errors, question_reports
    

def get_student_scores(ready_course):
    
    now = datetime.now()
    exams = Exam.objects.values('title', 'total_score').filter(~Q(exam_type='survey'), course=ready_course, is_deleted=0, section__is_deleted=0, live_datetime__lt=now).order_by('due_date')
    student_scores = ExamScore.objects.values('student__username', 'student__first_name', 'student__last_name', 'exam__title', 'score').select_related('student', 'exam').filter(~Q(exam__exam_type='survey'), course=ready_course, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now).order_by('student__username', 'exam__partial_credit_deadline')
    
    return exams, student_scores
        
    
def store_answer(tally, question, answer):

    if question in tally:
        tally[question]['+total+'] += 1
    else:
        tally[question] = {}
        tally[question]['+total+'] = 1

    if answer and answer not in tally[question]:
        tally[question][answer] = {}
        tally[question][answer] = 1                    
    elif answer:
        tally[question][answer] += 1
        
    return tally


def compute_score_summative(first_correct_attempt_number, first_correct_attempt_time_created, resubmission_penalty, submissions_permitted, grace_deadline, partial_credit_deadline, late_penalty):
    if (first_correct_attempt_number > submissions_permitted):
        return (0.0, 0.0)
        
    score = 1.0 - (first_correct_attempt_number - 1) * resubmission_penalty
    if score < 0:
        score = 0.0
    
    score_after_late_penalty = score
    # Apply late penalty if necessary
    if first_correct_attempt_time_created > partial_credit_deadline:
        if partial_credit_deadline: score_after_late_penalty = 0
    elif first_correct_attempt_time_created > grace_deadline:
        if grace_deadline: score_after_late_penalty = score * (1-late_penalty)
    
    return (score, score_after_late_penalty)
    
def median(l):
    if len(l) == 0: return None
    
    l = sorted(l)
    if (len(l)%2) == 0: return (l[len(l)/2] + l[(len(l)-1)/2]) / 2.0
    else:
        return l[(len(l)-1)/2]
        
def format_datetime(dt):
    if dt:
        return "%s-%s-%s at %s:%s" % (dt.year, dt.month, dt.day, dt.hour, dt.minute)
    else:
        return ""
        
def get_most_freq_inc_attempts(attempts, completes):
    incorrect_attempts_freqs = {}
    num_incorrect_attempts = 0
    for i in range(len(attempts)):
        if completes[i] == 0:
            if not attempts[i] in incorrect_attempts_freqs:
                incorrect_attempts_freqs[attempts[i]] = 0
            incorrect_attempts_freqs[attempts[i]] += 1
            num_incorrect_attempts += 1
            
    if num_incorrect_attempts > 20: # Results may not make sense for very few incorrect attempts
        sorted_tuples = sorted(incorrect_attempts_freqs.iteritems(), key = itemgetter(1), reverse = True)
        num_tuples = len(sorted_tuples)
        output_tuples = []
        for i in range(num_tuples):
            sorted_tuples[i] = (sorted_tuples[i][0], 100.0 * sorted_tuples[i][1] / num_incorrect_attempts)
            if sorted_tuples[i][1] > 5 and i <=3:
                output_tuples.append(sorted_tuples[i])
    
        return output_tuples
    else:
        return []