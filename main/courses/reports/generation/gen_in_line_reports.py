from __future__ import division
from c2g.models import Exam, ExamScore
from c2g.readonly import use_readonly_database
from django.db.models import Count, Q
from datetime import datetime
from courses.reports.generation.get_quiz_data import get_student_scores
from courses.reports.generation.gen_quiz_summary_report import construct_scores_dict

@use_readonly_database
def gen_spec_in_line_report(report_name, course, username, green_param, blue_param):

    if report_name == 'quizzes_summary': 
        
        now = datetime.now()       
        exams = Exam.objects.values('title').filter(~Q(exam_type='survey'), course=course, is_deleted=0, section__is_deleted=0, live_datetime__lt=now, invideo=0).order_by('title')

        headings = {}
        count_gt_67 = {}
        count_gt_34 = {}
        count_lt_34 = {}
        row_color = {}
        
        headings = ['Quiz Title', '# Students <33%', '# Students >33%', '# Students >67%']

        students_gt_67 = ExamScore.objects.values('exam__title').select_related('student', 'exam').filter(~Q(exam__exam_type='survey'), course=course, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now, exam__invideo=0).annotate(num_students=Count('student')).extra(where=["total_score*(66.7/100) <= score"])
        for row in students_gt_67:
            count_gt_67[row['exam__title']] = row['num_students']
        
        students_gt_34 = ExamScore.objects.values('exam__title').select_related('student', 'exam').filter(~Q(exam__exam_type='survey'), course=course, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now, exam__invideo=0).annotate(num_students=Count('student')).extra(where=["total_score*(33.4/100) <= score"])
        for row in students_gt_34:
            count_gt_34[row['exam__title']] = row['num_students']
            
        students_lt_34 = ExamScore.objects.values('exam__title').select_related('student', 'exam').filter(~Q(exam__exam_type='survey'), course=course, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now, exam__invideo=0).annotate(num_students=Count('student')).extra(where=["total_score*(33.4/100) >= score"])
        for row in students_lt_34:
            count_lt_34[row['exam__title']] = row['num_students']            
        
        for exam in exams:
            total = 0
            total_gt_67 = 0
                
            total = count_gt_34.setdefault(exam['title'], 0)
            total += count_lt_34.setdefault(exam['title'], 0)               
            
            total_gt_67 = count_gt_67.setdefault(exam['title'], 0)
            
            if total_gt_67 > 0 and ((total_gt_67/total)*100 >= int(green_param)):
                row_color[exam['title']] = "green"
            elif (total_gt_67 > 0) and ((total_gt_67/total)*100 >= int(blue_param)):
                row_color[exam['title']] = "blue"
            else:
                row_color[exam['title']] = "red"
        
        report_results = {}        
        report_results['headings'] = headings
        report_results['exam_titles'] = exams
        report_results['count_gt_67'] = count_gt_67
        report_results['count_gt_34'] = count_gt_34
        report_results['count_lt_34'] = count_lt_34
        report_results['row_color'] = row_color
        
        return report_results
    
    elif report_name == 'student_scores':
        
        exams, student_scores = get_student_scores(course, username)
        scores_dict = construct_scores_dict(student_scores)
        
        titles = ["", "Title"]
        max_scores = ["", "Max Score"]
        for exam in exams:
            titles += [exam['title']]
            max_scores += [exam['total_score']]
            
        row = []
        rows = []
        for username, scores in sorted(scores_dict.iteritems()):
            row += [username]
            row += [scores['name']]
            for title in titles:
                if scores.get(title, False):
                    row += [str(scores.get(title))]
                elif titles.index(title) not in [0, 1]:
                    row += [""]
            
            rows.append(row)
            row = []
         
        report_results = {}
        report_results['headings'] = titles
        report_results['max_scores'] = max_scores
        report_results['rows'] = rows
        
        return report_results
        
