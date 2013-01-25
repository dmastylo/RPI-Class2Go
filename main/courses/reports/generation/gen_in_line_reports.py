from c2g.models import Exam, ExamScore
from django.db.models import Count, Q
from datetime import datetime

def gen_spec_in_line_report(report_name, course):

    if report_name == 'quizzes_summary': 
        
        now = datetime.now()       
        exams = Exam.objects.values('title').filter(~Q(exam_type='survey'), course=course, is_deleted=0, section__is_deleted=0, live_datetime__lt=now).order_by('due_date')

        headings = {}
        count_gt_67 = {}
        count_gt_34 = {}
        count_lt_34 = {}
        
        headings = ['Quiz Title', '# Students <33%', '# Students >33%', '# Students >67%']

        students_gt_67 = ExamScore.objects.values('exam__title').select_related('student', 'exam').filter(~Q(exam__exam_type='survey'), course=course, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now).annotate(num_students=Count('student')).extra(where=["total_score*(66.7/100) <= score"])
        for row in students_gt_67:
            count_gt_67[row['exam__title']] = row['num_students']
        
        students_gt_34 = ExamScore.objects.values('exam__title').select_related('student', 'exam').filter(~Q(exam__exam_type='survey'), course=course, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now).annotate(num_students=Count('student')).extra(where=["total_score*(33.4/100) <= score"])
        for row in students_gt_34:
            count_gt_34[row['exam__title']] = row['num_students']
            
        students_lt_34 = ExamScore.objects.values('exam__title').select_related('student', 'exam').filter(~Q(exam__exam_type='survey'), course=course, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now).annotate(num_students=Count('student')).extra(where=["total_score*(33.4/100) >= score"])
        for row in students_lt_34:
            count_lt_34[row['exam__title']] = row['num_students']            
        
        report_results = {}        
        report_results['headings'] = headings
        report_results['exam_titles'] = exams
        report_results['count_gt_67'] = count_gt_67
        report_results['count_gt_34'] = count_gt_34
        report_results['count_lt_34'] = count_lt_34
        
        return report_results