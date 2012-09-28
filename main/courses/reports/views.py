from courses.reports.data_aggregation import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from courses.actions import auth_is_course_admin_view_wrapper
from storages.backends.s3boto import S3BotoStorage
from database import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME

@auth_is_course_admin_view_wrapper
def main(request, course_prefix, course_suffix):
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    
    # Read a list of all reports for that course that are on the server
    dashboard_csv_reports = secure_file_storage.listdir("%s/%s/reports/dashboard/csv" % (course_prefix, course_suffix) )
    dashboard_txt_reports = secure_file_storage.listdir("%s/%s/reports/dashboard/txt" % (course_prefix, course_suffix) )
    course_quizzes_csv_reports = secure_file_storage.listdir("%s/%s/reports/course_quizzes/csv" % (course_prefix, course_suffix) )
    course_quizzes_txt_reports = secure_file_storage.listdir("%s/%s/reports/course_quizzes/txt" % (course_prefix, course_suffix) )
    quiz_data_csv_reports = secure_file_storage.listdir("%s/%s/reports/quiz_data/csv" % (course_prefix, course_suffix) )
    quiz_data_txt_reports = secure_file_storage.listdir("%s/%s/reports/quiz_data/txt" % (course_prefix, course_suffix) )
    
    dashboard_reports = []
    
    
    return render_to_response('reports/main.html', {'common_page_data':request.common_page_data, 'dashboard_reports': dashboard_reports, 'course_quizzes_reports': course_quizzes_reports, 'quiz_data_reports': quiz_data_reports }, context_instance=RequestContext(request))
