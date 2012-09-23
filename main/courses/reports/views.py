from courses.reports.data_aggregation import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from courses.actions import auth_is_course_admin_view_wrapper

@auth_is_course_admin_view_wrapper
def main(request, course_prefix, course_suffix):
    dashboard_data = get_dashboard_data(request.common_page_data['draft_course'])
    return render_to_response('reports/main.html', {'common_page_data':request.common_page_data, 'dd':dashboard_data}, context_instance=RequestContext(request))
