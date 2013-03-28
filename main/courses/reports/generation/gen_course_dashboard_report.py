from c2g.models import *
from django.contrib.auth.models import User,Group
from datetime import datetime, timedelta
from courses.reports.generation.C2GReportWriter import *


def gen_course_dashboard_report(ready_course, save_to_s3=False):
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s-Dashboard.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix)
    s3_filepath = "%s/%s/reports/dashboard/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    # Title
    rw.write(content = ["Dashboard for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    
    # Members
    num_prof = ready_course.instructor_group.user_set.all().count()
    num_stud = ready_course.student_group.user_set.all().count()
    num_tas = ready_course.tas_group.user_set.all().count()
    num_rota = ready_course.readonly_tas_group.user_set.all().count()
    
    rw.write(content = ["Members"])
    rw.write(content = ["Students", num_stud, "Professors", num_prof, "TAs", num_tas, "Readonly TAs", num_rota], indent = 1, nl = 1)
    
    # Content
    live_exam_objects = Exam.objects.getByCourse(course=ready_course)
    all_exam_objects = Exam.objects.getByCourse(course=ready_course.image)
    exam_types = [li[0] for li in Exam.EXAM_TYPE_CHOICES]
    exam_content = {}
    for exam_type in exam_types:
        content_tuple = (all_exam_objects.filter(exam_type=exam_type), live_exam_objects.filter(exam_type=exam_type))
        exam_content[exam_type] = content_tuple

    num_all_formative_problem_sets = exam_content["problemset"][0].filter(assessment_type="formative").count()
    num_live_formative_problem_sets = exam_content["problemset"][1].filter(assessment_type="formative").count()
    num_all_summative_problem_sets = exam_content["problemset"][0].filter(assessment_type="summative").count()
    num_live_summative_problem_sets = exam_content["problemset"][1].filter(assessment_type="summative").count()
    num_all_videos = Video.objects.getByCourse(course=ready_course.image).count()
    live_videos = Video.objects.getByCourse(course=ready_course)
    num_live_videos = live_videos.count()
    num_all_pages = AdditionalPage.objects.getByCourse(course=ready_course.image).count()
    live_additional_pages = AdditionalPage.objects.getByCourse(course=ready_course)
    num_live_pages = live_additional_pages.count()
    num_all_files = File.objects.getByCourse(course=ready_course.image).count()
    num_live_files = File.objects.getByCourse(course=ready_course).count()
    
    rw.write(content = ["Content"])
    rw.write(content = ["Formative Quizzes", "Summative Quizzes", "Interactive Exercises", "Exams", "Surveys",  "Videos", "Content Pages", "Files"], indent = 2)
    rw.write(content = ["All", num_all_formative_problem_sets, num_all_summative_problem_sets, exam_content["interactive_exercise"][0].count(), exam_content["exam"][0].count(), exam_content["survey"][0].count(), num_all_videos, num_all_pages, num_all_files], indent = 1)
    rw.write(content = ["Live", num_live_formative_problem_sets, num_live_summative_problem_sets, exam_content["interactive_exercise"][1].count(), exam_content["exam"][1].count(), exam_content["survey"][1].count(), num_live_videos, num_live_pages, num_live_files], indent = 1)
    
    # Activity
    rw.write(content = ["Page Visits (Only live items are shown)"], nl = 1)

    visits = {}
    for exam_type in exam_types:
        visits[Exam.Exam_HUMAN_TYPES_PLURAL[exam_type]] = get_visit_information(ready_course, exam_content[exam_type][1], exam_type)
    visits["Videos"] = get_visit_information(ready_course, live_videos, 'video')
    visits["Content pages"] = get_visit_information(ready_course, live_additional_pages, 'additional_page')
    visits["Forum"] = get_visit_information(ready_course, None, 'forum')

    content_types = ["Forum", "Quizzes", "Interactive Exercises", "Exams", "Surveys", "Videos", "Content pages"]    
    for content_type in content_types:
        rw.write(content = [content_type], indent = 1)
        if content_type == "Forum":
            rw.write(content = ["", "", "", "Past day total", "Past day unique", "", "Past week total", "Past week unique", "", "all_time_total", "all_time_unique"], indent = 1)
            rw.write(content = ["", "", "", visits["Forum"][0]['past_day_total'], visits["Forum"][0]['past_day_unique'], "", visits["Forum"][0]['past_week_total'], visits["Forum"][0]['past_week_unique'], "", visits["Forum"][0]['all_time_total'], visits["Forum"][0]['all_time_unique']], indent = 1)
        else:
            if len(visits[content_type]) > 0:
                rw.write(content = ["URL ID", "Title", "", "Past day total", "Past day unique", "", "Past week total", "Past week unique", "", "all_time_total", "all_time_unique"], indent = 1)
                for item in visits[content_type]:
                    rw.write(content = [item['item'].slug, item['item'].title, "", item['past_day_total'], item['past_day_unique'], "", item['past_week_total'], item['past_week_unique'], "", item['all_time_total'], item['all_time_unique']], indent = 1)                
            else:
                rw.write(content = ["No live " + content_type.lower() + " yet."], indent = 2)
        rw.write([""])
    
    report_content = rw.writeout()
    return {'name': "%02d_%02d_%02d__%02d_%02d_%02d-%s-Dashboard.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix), 'content': report_content, 'path': s3_filepath}
    

def get_visit_information(ready_course, items, page_type):
    if items == None:
        visits_ = PageVisitLog.objects.filter(course=ready_course, page_type = page_type)
        visit_counts = analyze_visits(visits_)
        return [dict({'item': None}.items() + visit_counts.items())]
    else:
        visits = []
        for item in items:
            visits_ = PageVisitLog.objects.filter(course=ready_course, page_type = page_type, object_id=str(item.id))
            visit_counts = analyze_visits(visits_)
            visits.append(dict({'item': item}.items() + visit_counts.items()))
        return visits
            

def analyze_visits(visits_):
    now = datetime.now()
    now_minus_24_hours = now - timedelta(days=1)
    now_minus_1_week = now - timedelta(days=7)
    past_24_hours_total_visitors = visits_.filter(time_created__gt = now_minus_24_hours).values_list('user', flat=True)
    past_1_week_total_visitors = visits_.filter(time_created__gt = now_minus_1_week).values_list('user', flat=True)
    all_time_total_visitors = visits_.values_list('user', flat=True)
    
    past_24_hours_unique_visitors = set(past_24_hours_total_visitors)
    past_1_week_unique_visitors = set(past_1_week_total_visitors)
    all_time_unique_visitors = set(all_time_total_visitors)
    
    return {'past_day_total': len(past_24_hours_total_visitors), 'past_week_total': len(past_1_week_total_visitors), 'all_time_total': len(all_time_total_visitors), 'past_day_unique': len(past_24_hours_unique_visitors), 'past_week_unique': len(past_1_week_unique_visitors), 'all_time_unique': len(all_time_unique_visitors)}
    
