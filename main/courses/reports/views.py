import re
import mimetypes
from c2g.models import *
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from courses.actions import auth_is_course_admin_view_wrapper
from courses.reports.tasks import generate_and_email_reports
from storages.backends.s3boto import S3BotoStorage
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
from courses.reports.generation.gen_in_line_reports import *

secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
re_prog = re.compile(r'([\d]{4})_([\d]{2})_([\d]{2})__([\d]{2})_([\d]{2})_([\d]{2})')
    
@auth_is_course_admin_view_wrapper
def main(request, course_prefix, course_suffix):
    
    course = request.common_page_data['ready_course']
    course_prefix = course.handle.split('--')[0]
    course_suffix = course.handle.split('--')[1]
    
    
    # 1- List all problem sets and videos, since instructors may let something fo non-live then try to get its report. If instructors try to generate a report for something that doesn't have a live instance, we will write that in the report
    videos = Video.objects.getByCourse(course=course.image).order_by('-live_datetime', 'title')
    exams = Exam.objects.getByCourse(course=course.image).order_by('-live_datetime', 'title')
    surveys = exams.filter(exam_type='survey')
    
    # 2- Read a list of all reports for that course that are on the server
    dashboard_reports = list_reports_in_dir("%s/%s/reports/dashboard/" % (course_prefix, course_suffix))
    video_full_reports = list_reports_in_dir("%s/%s/reports/videos/" % (course_prefix, course_suffix))
    video_summ_reports = list_reports_in_dir("%s/%s/reports/videos_summary/" % (course_prefix, course_suffix))
    class_rosters = list_reports_in_dir("%s/%s/reports/class_roster/" % (course_prefix, course_suffix))
    
    #For new assessment reports
    course_assessment_reports = list_reports_in_dir("%s/%s/reports/course_assessments/" % (course_prefix, course_suffix))
    assessment_full_reports = list_reports_in_dir("%s/%s/reports/problemsets/" % (course_prefix, course_suffix))
    assessment_summ_reports = list_reports_in_dir("%s/%s/reports/problemsets_summary/" % (course_prefix, course_suffix))
    survey_summ_reports = list_reports_in_dir("%s/%s/reports/survey_summary/" % (course_prefix, course_suffix))
    assessment_student_scores_reports = list_reports_in_dir("%s/%s/reports/assessment_student_scores/" % (course_prefix, course_suffix))
    
    
    # 3- Divide ps and video reports into lists of dicts ready for grouped display by object
    vd_quiz_full_reports_list_of_dicts = ClassifyReportsBySlug(videos, video_full_reports)
    vd_quiz_summ_reports_list_of_dicts = ClassifyReportsBySlug(videos, video_summ_reports)
    
    assessment_full_reports_list_of_dicts = ClassifyReportsBySlug(exams, assessment_full_reports)
    assessment_summ_reports_list_of_dicts = ClassifyReportsBySlug(exams, assessment_summ_reports)
    survey_summ_reports_list_of_dicts = ClassifyReportsBySlug(surveys, survey_summ_reports)
    
    
    # 4- Render to response
    return render_to_response('reports/main.html', {
        'common_page_data':request.common_page_data,
        'dashboard_reports': dashboard_reports,
        'class_rosters': class_rosters,
        'vd_quiz_full_reports': vd_quiz_full_reports_list_of_dicts,
        'vd_quiz_summ_reports': vd_quiz_summ_reports_list_of_dicts,
        'videos': videos.order_by('title'),
        'course_assessment_reports': course_assessment_reports,
        'exams': exams.order_by('title'),
        'assessment_full_reports': assessment_full_reports_list_of_dicts,
        'assessment_summ_reports': assessment_summ_reports_list_of_dicts,
        'survey_summ_reports': survey_summ_reports_list_of_dicts,
        'surveys': surveys.order_by('title'),
        'assessment_student_scores_reports': assessment_student_scores_reports,
    }, context_instance=RequestContext(request))
    
    
def ClassifyReportsBySlug(objs, reports):
    reports_dict = {}
    for obj in objs: reports_dict[obj.slug] = {'title': obj.title, 'reports': []}
    
    for report in reports:
        slug = get_slug_from_report_name(report['s3_name'])
        if slug in reports_dict:
            reports_dict[slug]['reports'].append(report)
        
    reports_list_of_dicts = []
    for obj in objs:
        reports_list_of_dicts.append(reports_dict[obj.slug])
        
    return reports_list_of_dicts
        

#@auth_is_course_admin_view_wrapper
def generate_report(request):
    report_type = request.POST["type"]
    course_handle = request.POST["course_handle"]
    course_handle_pretty = course_handle.replace('--','-')
    
    email_message = "The report is attached. You can also download it by going to the reports page under Course Administration->Reports, or by visiting https://class.stanford.edu/%s/browse_reports." % course_handle.replace('--', '/')
    attach_reports_to_email = True
    
    if report_type == 'dashboard':
        email_title = "[Class2Go] Dashboard Report for %s" % course_handle_pretty
        req_reports = [{'type': 'dashboard'}]
        
    elif report_type == 'video_full':
        slug = request.POST["slug"]
        email_title = "[Class2Go] Video Full Report for %s %s" % (course_handle_pretty, slug)
        # TODO: Remove the following message and attachment flag override after report email attachment is fixed
        attach_reports_to_email = False
        email_message = "The report has been generated. You can download it by going to the reports page under Course Administration->Reports, or by visiting https://class.stanford.edu/%s/browse_reports." % course_handle.replace('--', '/')
        req_reports = [{'type': 'video_full', 'slug': slug}]
        
    elif report_type == 'video_summary':
        slug = request.POST["slug"]
        email_title = "[Class2Go] Video Summary Report for %s %s" % (course_handle_pretty, slug)
        req_reports = [{'type': 'video_summary', 'slug': slug}]
        
    elif report_type == 'class_roster':
        email_title = "[Class2Go] Class Roster for %s" % (course_handle_pretty)
        req_reports = [{'type': 'class_roster'}]
    
    #Reports for the new assessments
    elif report_type == 'course_assessments':
        email_title = "[Class2Go] Course Assessments Report for %s" % course_handle_pretty
        req_reports = [{'type': 'course_assessments'}]
    
    elif report_type == 'assessment_full':
        slug = request.POST["slug"]
        email_title = "[Class2Go] Assessment Full Report for %s %s" % (course_handle_pretty, slug)
        # TODO: Remove the following message  and attachment flag override after report email attachment is fixed
        attach_reports_to_email = False
        email_message = "The report has been generated. You can download it by going to the reports page under Course Administration->Reports, or by visiting https://class.stanford.edu/%s/browse_reports." % course_handle.replace('--', '/')
        req_reports = [{'type': 'assessment_full', 'slug': slug}]
    
    elif report_type == 'assessment_summary':
        slug = request.POST["slug"]
        email_title = "[Class2Go] Assessment Summary Report for %s %s" % (course_handle_pretty, slug)
        req_reports = [{'type': 'assessment_summary', 'slug': slug}]
        
    elif report_type == 'survey_summary':
        slug = request.POST["slug"]
        email_title = "[Class2Go] Survey Summary Report for %s %s" % (course_handle_pretty, slug)
        req_reports = [{'type': 'survey_summary', 'slug': slug}]
    
    elif report_type == 'assessment_student_scores':
        email_title = "[Class2Go] Assessment Student Scores Report for %s" % (course_handle_pretty)
        req_reports = [{'type': 'assessment_student_scores'}]    
    
    generate_and_email_reports.delay(request.user.username, course_handle, req_reports, email_title, email_message, attach_reports_to_email)
    
    return redirect(request.META.get('HTTP_REFERER', None))


@auth_is_course_admin_view_wrapper  
def download_report(request, course_prefix, course_suffix, report_subfolder, report_name):
    #secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    report_path = "%s/%s/reports/%s/%s" % (course_prefix, course_suffix, report_subfolder, report_name)
    
    try:
        report_file= secure_file_storage.open(report_path, 'rb')
    except:
        return Http404
    
    report_content = report_file.read()
    
    if report_subfolder in ['problemsets_summary', 'videos_summary']:
        report_name = report_name[:-4] + '_summary.csv'
    
    response = HttpResponse(report_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + report_name
    response['Content-Length'] = str(len(report_content))
    
    return response


def list_reports_in_dir(dirname):
    report_s3list = secure_file_storage.listdir(dirname)
    report_s3list = sorted(report_s3list[1], reverse=True)
    
    reports = []
    for rep_item in report_s3list:
        if len(rep_item) > 0 and isinstance(rep_item, unicode):
            res = re_prog.match(rep_item)
            if res:
                dt_parts = res.groups(0)
                reports.append({'name': "%s-%s-%s at %s:%s" % (dt_parts[1], dt_parts[2], dt_parts[0], dt_parts[3], dt_parts[4]), 's3_name': rep_item})
    
    return reports

def get_report_date(rep_name):
    return {'year': rep_name[0:4], 'month': rep_name[6:8], 'day': rep_name[9:11], 'hour': rep_name[13:15], 'minute': rep_name[16:18], 'second': rep_name[19:21]}

    
def get_slug_from_report_name(rep_name):
    return rep_name[21:-4]


@auth_is_course_admin_view_wrapper    
def generate_in_line_report(request, course_prefix, course_suffix):
    
    if request.POST.get("report_name", False): 
        report_name = request.POST["report_name"]
    else:
        report_name = ""
    
    course = request.common_page_data['ready_course']
    
    report_label = None
    report_data = {}
    headings = {}
    column1 = {}
    column2 = {}
    column3 = {}
    column4 = {}
    column5 = {}
    column6 = {}
    
    we_have_data = False
    if report_name == 'quizzes_summary':
        report_data = gen_spec_in_line_report(report_name, course)
        if report_data:
            report_label = "Quizzes Summary"
            headings = report_data['headings']
            column1 = report_data['exam_titles']
            column2 = report_data['count_lt_34']
            column3 = report_data['count_gt_34']
            column4 = report_data['count_gt_67']
            we_have_data = True

    return render_to_response('reports/in_line.html', {
        'common_page_data':request.common_page_data,
        'we_have_data':we_have_data,
        'report_label':report_label,
        'headings':headings,
        'column1':column1,
        'column2':column2,
        'column3':column3,
        'column4':column4,
        'column5':column5,
        'column6':column6,
    }, context_instance=RequestContext(request))
    
