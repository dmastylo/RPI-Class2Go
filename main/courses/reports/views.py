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

secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
re_prog = re.compile(r'([\d]{4})_([\d]{2})_([\d]{2})__([\d]{2})_([\d]{2})_([\d]{2})')
    
@auth_is_course_admin_view_wrapper
def main(request, course_prefix, course_suffix):
    
    course = request.common_page_data['ready_course']
    course_prefix = course.handle.split('--')[0]
    course_suffix = course.handle.split('--')[1]
    
    # List all problem sets and videos, since instructors may let something fo non-live then try to get its report. If instructors try to generate a report for something that doesn't have a live instance, we will write that in the report
    problemsets = ProblemSet.objects.getByCourse(course=course.image).order_by('-live_datetime', 'title')
    videos = Video.objects.getByCourse(course=course.image).order_by('-live_datetime', 'title')
    
    # Read a list of all reports for that course that are on the server
    dashboard_reports = list_reports_in_dir("%s/%s/reports/dashboard/" % (course_prefix, course_suffix))
    course_quizzes_reports = list_reports_in_dir("%s/%s/reports/course_quizzes/" % (course_prefix, course_suffix))
    problemset_reports = list_reports_in_dir("%s/%s/reports/problemsets/" % (course_prefix, course_suffix))
    video_reports = list_reports_in_dir("%s/%s/reports/videos/" % (course_prefix, course_suffix))
    
    ps_quiz_data_reports_dict = {}
    for ps in problemsets: ps_quiz_data_reports_dict[ps.slug] = {'title': ps.title, 'reports': []}
    
    for problemset_report in problemset_reports:
        report_slug = get_quiz_slug(problemset_report['s3_name'])
        ps_quiz_data_reports_dict[report_slug]['reports'].append(problemset_report)
        
    ps_quiz_data_reports_list = []
    for ps in problemsets:
        ps_quiz_data_reports_list.append(ps_quiz_data_reports_dict[ps.slug])
        
    vd_quiz_data_reports_dict = {}
    for vd in videos: vd_quiz_data_reports_dict[vd.slug] = {'title': vd.title, 'reports': []}
    
    for video_report in video_reports:
        report_slug = get_quiz_slug(video_report['s3_name'])
        vd_quiz_data_reports_dict[report_slug]['reports'].append(video_report)
        
    vd_quiz_data_reports_list = []
    for vd in videos:
        vd_quiz_data_reports_list.append(vd_quiz_data_reports_dict[vd.slug])
        
    return render_to_response('reports/main.html', {
        'common_page_data':request.common_page_data,
        'dashboard_reports': dashboard_reports,
        'course_quizzes_reports': course_quizzes_reports,
        'vd_quiz_data_reports': vd_quiz_data_reports_list,
        'ps_quiz_data_reports': ps_quiz_data_reports_list,
        'videos': videos.order_by('title'),
        'problemsets': problemsets.order_by('title'),
    }, context_instance=RequestContext(request))

#@auth_is_course_admin_view_wrapper
def generate_report(request):
    report_type = request.POST["type"]
    course_handle = request.POST["course_handle"]
    course_handle_pretty = course_handle.replace('--','-')
    if report_type == 'dashboard':
        email_title = "[Class2Go] Dashboard Report for %s" % course_handle_pretty
        req_reports = [{'type': 'dashboard'}]
        
    elif report_type == 'course_quizzes':
        email_title = "[Class2Go] Course Quizzes Report for %s" % course_handle_pretty
        req_reports = [{'type': 'course_quizzes'}]
        
    elif report_type == 'problemset':
        slug = request.POST["slug"]
        email_title = "[Class2Go] Problemset Report for %s %s" % (course_handle_pretty, slug)
        req_reports = [{'type': 'problemset', 'slug': slug}]
        
    elif report_type == 'video':
        slug = request.POST["slug"]
        email_title = "[Class2Go] Video Report for %s %s" % (course_handle_pretty, slug)
        req_reports = [{'type': 'video', 'slug': slug}]
    
    email_message = "The report is attached. You can also download it by going to the reports page under Course Administration->Reports, or by visiting https://class.stanford.edu/%s/browse_reports." % course_handle.replace('--', '/')
    
    #generate_and_email_reports.delay(request.user.username, course_handle, req_reports, email_title, email_message)
    generate_and_email_reports(request.user.username, course_handle, req_reports, email_title, email_message)
    
    return redirect(request.META.get('HTTP_REFERER', None))


@auth_is_course_admin_view_wrapper  
def download_report(request, course_prefix, course_suffix, report_type, report_name):
    #secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    report_path = "%s/%s/reports/%s/%s" % (course_prefix, course_suffix, report_type, report_name)
    
    try:
        report_file= secure_file_storage.open(report_path, 'rb')
    except:
        return Http404
    
    report_content = report_file.read()
    
    #mimetype_guess = mimetypes.guess_type(report_name)
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

    
def get_quiz_slug(rep_name):
    return rep_name[21:-4]