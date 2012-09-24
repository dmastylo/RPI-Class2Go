from c2g.models import *
from datetime import datetime, timedelta
import time
import math
from django.db.models import Avg
from courses.reports.data_aggregation.utility_functions import *

def get_course_dashboard_report_data(draft_course):
    ready_course = draft_course.image
    
    dd = {'now': datetime.now(), 'ap':{}, 'ps':{}, 'vd':{}, 'fm':{}}
    
    ### Gets summary dashboard data ###
    # This is all we want to render on the reports page. Additional details such as page visits ... etc are available through the _detailed version.
    # We do this to prevent the instructor from having to wait for a long time everytime they visit the report page.
    
    # Get counts of course instructors, TAs, read-only TAs, and students
    instructors = draft_course.instructor_group.user_set.all()
    students = draft_course.student_group.user_set.all()
    tas = draft_course.tas_group.user_set.all()
    readonly_tas = draft_course.readonly_tas_group.user_set.all()
    
    dd['num_instructors'] = instructors.count()
    dd['num_students'] = students.count()
    dd['num_tas'] = tas.count()
    dd['num_readonly_tas'] = readonly_tas.count()
    
    # Get list of all videos, problem sets, additional pages, and files
    dd['ap']['list'] = []
    dd['ps']['list'] = []
    dd['vd']['list'] = []
    dd['fl'] = {'num': File.objects.getByCourse(ready_course).count(), 'num_live': File.objects.getByCourse(ready_course).filter(live_datetime__lt=datetime.now()).count()}
    
    for ap in AdditionalPage.objects.getSectionPagesByCourse(ready_course).order_by('-live_datetime'):
        dd['ap']['list'].append({'object': ap})
        
    for ps in ProblemSet.objects.getByCourse(ready_course).order_by('-live_datetime'):
        dd['ps']['list'].append({'object': ps})
        
    for vd in Video.objects.getByCourse(ready_course).order_by('-live_datetime'):
        dd['vd']['list'].append({'object': vd})
    
    dd['ap']['num'] = AdditionalPage.objects.getSectionPagesByCourse(draft_course).count()
    dd['ps']['num'] = ProblemSet.objects.getByCourse(draft_course).count()
    dd['vd']['num'] = Video.objects.getByCourse(draft_course).count()
    
    dd['ap']['num_live'] = AdditionalPage.objects.getSectionPagesByCourse(ready_course).count()
    dd['ps']['num_live'] = ProblemSet.objects.getByCourse(ready_course).count()
    dd['vd']['num_live'] = Video.objects.getByCourse(ready_course).count()
    
    dd['ps']['num_formative'] = ProblemSet.objects.filter(course=draft_course, assessment_type='formative').count()
    dd['ps']['num_formative_live'] = ProblemSet.objects.filter(course=ready_course, assessment_type='formative').count()
                
    dd['ps']['num_summative'] = ProblemSet.objects.filter(course=draft_course, assessment_type='summative').count()
    dd['ps']['num_summative_live'] = ProblemSet.objects.filter(course=ready_course, assessment_type='summative').count()
    
    now_minus_one_day = dd['now']-timedelta(days=1)
    now_minus_one_week = dd['now']-timedelta(days=7)
    
    # Get visits for additional pages, problem sets, videos, and the forum
    ap_visits = PageVisitLog.objects.filter(course=ready_course, page_type='additional_page')
    ps_visits = PageVisitLog.objects.filter(course=ready_course, page_type='problemset')
    vd_visits = PageVisitLog.objects.filter(course=ready_course, page_type='video')
    fm_visits = PageVisitLog.objects.filter(course=ready_course, page_type='forum')
    
    dd['ps']['aggr_visits'] = {'total': 0, 'unique': 0}
    dd['ap']['aggr_visits'] = {'total': 0, 'unique': 0}
    dd['vd']['aggr_visits'] = {'total': 0, 'unique': 0}
    
    for item in dd['ap']['list']:
        item['visits'] = {
            'total':{
                'past_24_hours': ap_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_day).count(),
                'past_week': ap_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_week).count(),
                'all_time': ap_visits.filter(object_id=str(item['object'].id)).count(),
            },
            'unique':{
                'past_24_hours': qs_unique_by_user(ap_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_day)).count(),
                'past_week': qs_unique_by_user(ap_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_week)).count(),
                'all_time': qs_unique_by_user(ap_visits.filter(object_id=str(item['object'].id))).count(),
            }
        }
        dd['ap']['aggr_visits']['total'] += item['visits']['total']['all_time']
        dd['ap']['aggr_visits']['unique'] += item['visits']['unique']['all_time']
        
    for item in dd['ps']['list']:
        item['visits'] = {
            'total':{
                'past_24_hours': ps_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_day).count(),
                'past_week': ps_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_week).count(),
                'all_time': ps_visits.filter(object_id=str(item['object'].id)).count(),
            },
            'unique':{
                'past_24_hours': qs_unique_by_user(ps_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_day)).count(),
                'past_week': qs_unique_by_user(ps_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_week)).count(),
                'all_time': qs_unique_by_user(ps_visits.filter(object_id=str(item['object'].id))).count(),
            }
        }
        dd['ps']['aggr_visits']['total'] += item['visits']['total']['all_time']
        dd['ps']['aggr_visits']['unique'] += item['visits']['unique']['all_time']
        
    for item in dd['vd']['list']:
        item['visits'] = {
            'total':{
                'past_24_hours': vd_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_day).count(),
                'past_week': vd_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_week).count(),
                'all_time': vd_visits.filter(object_id=str(item['object'].id)).count(),
            },
            'unique':{
                'past_24_hours': qs_unique_by_user(vd_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_day)).count(),
                'past_week': qs_unique_by_user(vd_visits.filter(object_id=str(item['object'].id), time_created__gte=now_minus_one_week)).count(),
                'all_time': qs_unique_by_user(vd_visits.filter(object_id=str(item['object'].id))).count(),
            }
        }
        dd['vd']['aggr_visits']['total'] += item['visits']['total']['all_time']
        dd['vd']['aggr_visits']['unique'] += item['visits']['unique']['all_time']
        
    dd['fm']['visits'] = {
        'total':{
            'past_24_hours': fm_visits.filter(time_created__gte=now_minus_one_day).count(),
            'past_week': fm_visits.filter(time_created__gte=now_minus_one_week).count(),
            'all_time': fm_visits.count(),
        },
        'unique':{
            'past_24_hours': qs_unique_by_user(fm_visits.filter(time_created__gte=now_minus_one_day)).count(),
            'past_week': qs_unique_by_user(fm_visits.filter(time_created__gte=now_minus_one_week)).count(),
            'all_time': qs_unique_by_user(fm_visits).count(),
        }
    }
    
    return dd