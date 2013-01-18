from c2g.models import Exam, ExamRecord
from django.db.models import Count
from datetime import datetime

def gen_spec_in_line_report(report_name, course):

    if report_name == 'interactive_quizzes_summary': 
        
        now = datetime.now()       
        exams = Exam.objects.values('title').filter(course=course, exam_type='interactive_exercise', is_deleted=0, section__is_deleted=0, live_datetime__lt=now).order_by('due_date')

        headings = {}
        count_gt_67 = {}
        count_gt_34 = {}
        count_lt_34 = {}
        
        headings = ['Quiz Title', '# Students <33%', '# Students >33%', '# Students >67%']

        attempts_gt_67 = ExamRecord.objects.values('exam__title').select_related('exam').filter(exam__course=course, exam__exam_type='interactive_exercise', complete=1, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now).annotate(num_students=Count('student')).extra(  where=["total_score*(66.7/100) <= score"])
        for attempt in attempts_gt_67:
            count_gt_67[attempt['exam__title']] = attempt['num_students']
        
        attempts_gt_34 = ExamRecord.objects.values('exam__title').select_related('exam').filter(exam__course=course, exam__exam_type='interactive_exercise', complete=1, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now).annotate(num_students=Count('student')).extra(  where=["total_score*(33.4/100) <= score"])
        for attempt in attempts_gt_34:
            count_gt_34[attempt['exam__title']] = attempt['num_students']
            
        attempts_lt_34 = ExamRecord.objects.values('exam__title').select_related('exam').filter(exam__course=course, exam__exam_type='interactive_exercise', complete=1, exam__is_deleted=0, exam__section__is_deleted=0, exam__live_datetime__lt=now).annotate(num_students=Count('student')).extra(  where=["total_score*(33.4/100) >= score"])
        for attempt in attempts_lt_34:
            count_lt_34[attempt['exam__title']] = attempt['num_students']            
        
        report_results = {}        
        report_results['headings'] = headings
        report_results['exam_titles'] = exams
        report_results['count_gt_67'] = count_gt_67
        report_results['count_gt_34'] = count_gt_34
        report_results['count_lt_34'] = count_lt_34
        
        return report_results