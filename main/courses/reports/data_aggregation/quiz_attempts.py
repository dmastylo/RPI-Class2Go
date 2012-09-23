from c2g.models import *
from datetime import datetime, timedelta
import time
import math
from django.db.models import Avg
from courses.reports.data_aggregation.utility_functions import *

def aggregate_quiz_attempts_report_data(ready_quiz, ex_att_dl):
    res_table = {}
    totals = {}
    
    exercises = []
    for ex_att_d in ex_att_dl:
        ex = ex_att_d['exercise']
        atts = ex_att_d['attempts']
        
        exercises.append(ex)
        
        for ai in range(atts.count()):
            is_fa = (ai == 0) or (atts[ai].student != atts[ai-1].student) # is first attempt
            is_la = (ai == atts.count()-1) or (atts[ai].student != atts[ai+1].student) # is last attempt
            
            if is_fa:
                fa_index = ai
                temp_tt2fca = 0
                score = 0
                student_attempts = []
                neglect_next_attempts = False
            
            if not neglect_next_attempts:
                att_number = ai - fa_index + 1 # The number of the att in the student's att seq
                student_attempts.append(atts[ai].attempt_content)
                temp_tt2fca += atts[ai].time_taken
            
            if atts[ai].complete == 1: neglect_next_attempts = True
            
            if is_la:
                # Compute score
                resubmission_penalty = 0
                submissions_permitted = sys.maxsize
                
                if isinstance(ready_quiz, ProblemSet) and (ready_quiz.assessment_type == 'summative'):
                    resubmission_penalty = ready_quiz.resubmission_penalty
                    submissions_permitted = ready_quiz.submissions_permitted
                    if submissions_permitted == 0: submissions_permitted = sys.maxsize
                    
                score = 1.0 - (resubmission_penalty/100.0)*att_number
                if (score < 0) or (att_number > submissions_permitted): score = 0
                
                mean_attempt_time = int(temp_tt2fca/(att_number))
                
                # Write the data to the student's row
                if not (atts[ai].student.username in res_table): res_table[atts[ai].student.username] = {}
                res_table[atts[ai].student.username][ex.id] = {'student':atts[ai].student, 'attempts': student_attempts, 'mean_attempt_time': str(mean_attempt_time), 'score': "%.2f" % score}
                
                # Add exercise score to the totals
                if not (atts[ai].student.username in totals): totals[atts[ai].student.username] = 0
                totals[atts[ai].student.username] += score
    
    return {'exercises': exercises, 'res_table': res_table, 'totals': totals}

def get_quiz_attempts_report_data(ready_quiz, order_by='time_created'):
    dl = []
    
    if isinstance(ready_quiz, Video):
        rlns = VideoToExercise.objects.filter(video=ready_quiz).order_by('video_time')
        for rln in rlns:
            attempts = ProblemActivity.objects.filter(video_to_exercise=rln).order_by(order_by, 'time_created').only('student', 'complete', 'count_hints', 'attempt_content', 'time_taken').select_related()
            dl.append({'exercise': rln.exercise, 'attempts': attempts})
    else:
        rlns = ProblemSetToExercise.objects.filter(problemSet=ready_quiz).order_by('number')
        for rln in rlns:
            attempts = ProblemActivity.objects.filter(problemset_to_exercise=rln).order_by(order_by, 'time_created').only('student', 'complete', 'count_hints', 'attempt_content', 'time_taken').select_related()
            dl.append({'exercise': rln.exercise, 'attempts': attempts})
    
    return dl
    