import sys
from c2g.models import *
from datetime import datetime, timedelta
import time
import math
from django.db.models import Avg
from courses.reports.data_aggregation.quiz_attempts import *
from courses.reports.data_aggregation.utility_functions import *

def get_course_quizzes_report_data(ready_course):
    all_quizzes_data = []
    
    course_students = ready_course.student_group.user_set.all()
    
    for ready_quiz in ProblemSet.objects.getByCourse(course=ready_course):
        all_quizzes_data.append(get_quiz_report_data(ready_quiz, course_students))
    
    for ready_quiz in Video.objects.getByCourse(course=ready_course):
        all_quizzes_data.append(get_quiz_report_data(ready_quiz, course_students))

    return all_quizzes_data
    
def get_quiz_report_data(ready_quiz, course_students):
    assessment_type = 'summative' if (isinstance(ready_quiz, ProblemSet) and (ready_quiz.assessment_type == 'summative')) else 'formative'
    ex_att_dl = get_quiz_attempts_report_data(ready_quiz, order_by='student') # List of dicts of {'exercise':..., 'attempts':...}
    quiz_total_scores = {}
    
    ### Data lists ###
        
    # Initialize data lists
    num_attempts = {}
    fca_number = {} # First correct attempt number
    attempt_times = {}
    total_time_to_fca = {}
    scores = {}
    icfa_contents = {} # Contents of incorrect first attempts
    
    for ex_att_d in ex_att_dl:
        ex = ex_att_d['exercise']
        num_attempts[ex.id] = []
        fca_number[ex.id] = []
        attempt_times[ex.id] = []
        total_time_to_fca[ex.id] = []
        scores[ex.id] = {}
        icfa_contents[ex.id] = []
        
    # Populate the data lists
    for ex_att_d in ex_att_dl:
        ex = ex_att_d['exercise']
        atts = ex_att_d['attempts']
        
        for ai in range(atts.count()):
            is_fa = (ai == 0) or (atts[ai].student != atts[ai-1].student) # is first attempt
            is_la = (ai == atts.count()-1) or (atts[ai].student != atts[ai+1].student) # is last attempt
            
            if is_fa: # At the start of every student's attempt sequence, set fa_index to the current index, set score to 0, and reset temp_tt2fca to 0
                fa_index = ai
                temp_tt2fca = 0
                score = 0
                if not atts[ai].complete: icfa_contents[ex.id].append(atts[ai].attempt_content) # If first attempt is not correct, register its content to fa_content
                
            att_number = ai - fa_index + 1 # The number of the att in the student's att seq
            temp_tt2fca += atts[ai].time_taken
            attempt_times[ex.id].append(atts[ai].time_taken)
            
            if atts[ai].complete: # When correct attempt is found, compute score (if summative PS) and register fca_number and total_time_fca
                fca_number[ex.id].append(att_number)
                
                total_time_to_fca[ex.id].append(temp_tt2fca)
                
                if assessment_type == 'summative':
                    resubmission_penalty = ready_quiz.resubmission_penalty
                    submissions_permitted = ready_quiz.submissions_permitted
                    if submissions_permitted == 0: submissions_permitted = sys.maxsize
                    if att_number > submissions_permitted: score = 0
                    else: score = 100 - att_number * resubmission_penalty
                    if score < 0: score = 0
                    score = score/100.0
                    
            
            if is_la: # Before leaving to the next student, register the total number of attempts consumed, and the student score if the quiz is a summ. ps.
                num_attempts[ex.id].append(att_number+1)
                if assessment_type == 'summative':
                    scores[ex.id][atts[ai].student.id] = score
                    if atts[ai].student.id in quiz_total_scores: quiz_total_scores[atts[ai].student.id] += score
                    else: quiz_total_scores[atts[ai].student.id] = 0
                        

    ### Create output data structure ###
    quiz_data = {'quiz': ready_quiz, 'has_attempts': False, 'exercises': []}
    
    for ex_att_d in ex_att_dl:
        ex = ex_att_d['exercise']
        atts = ex_att_d['attempts']
        att_count = atts.count()
        ex_data = {'exercise': ex, 'has_attempts': att_count > 0}
        
        if att_count == 0: continue
        
        quiz_data['has_attempts'] = True
        
        ex_data['num_attempts'] = att_count
        ex_data['num_unique_attempts'] = len(num_attempts[ex.id])
        
        if assessment_type == 'summative':
            ex_data['mean_score'] = sum(scores[ex.id].values())/ex_data['num_unique_attempts']
            ex_data['max_score'] = max(scores[ex.id].values())
        
        ex_data['num_students_with_correct_attempt'] = len(total_time_to_fca[ex.id])
        ex_data['mean_time_per_attempt'] = sum(attempt_times[ex.id])/len(attempt_times[ex.id])
            
        ex_data['num_students_with_correct_first_attempt'] = fca_number[ex.id].count(1)
        ex_data['num_students_with_correct_second_attempt'] = fca_number[ex.id].count(2)
        ex_data['num_students_with_correct_third_attempt'] = fca_number[ex.id].count(3)
        
        quiz_data['exercises'].append(ex_data)
    
    if assessment_type == 'summative' and quiz_data['has_attempts']:
        quiz_total_scores_list = quiz_total_scores.values()
        quiz_data['max_score'] = max(quiz_total_scores_list)
        quiz_data['mean_score'] = sum(quiz_total_scores_list)/len(quiz_total_scores_list)
    
    return quiz_data