from c2g.models import *
from django.contrib.auth.models import User,Group
from courses.reports.generation.C2GReportWriter import *
from c2g.readonly import use_readonly_database

@use_readonly_database
def gen_class_roster(ready_course, save_to_s3=False):
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s-Class-Roster.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix)
    s3_filepath = "%s/%s/reports/class_roster/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    # Title
    rw.write(content = ["Class Roster for %s (%s %d) as of %02d/%02d/%d" % (ready_course.title, ready_course.term.title(), ready_course.year, dt.month, dt.day, dt.year)], nl = 1)
    
    # Members
    students = ready_course.student_group.user_set.order_by('username').all().order_by('last_name').values_list('first_name', 'last_name', 'email', 'username')
    
    rw.write(content = ["Num. Students:", "", len(students)], nl=1)
    
    rw.write(content = ["First namme", "Last name", "Email", "Username"])
    for s in students:
        rw.write(content = [s[0], s[1], s[2], s[3]])
    
    report_content = rw.writeout()
    return {'name': "%02d_%02d_%02d__%02d_%02d_%02d-%s-Class-Roster.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix), 'content': report_content, 'path': s3_filepath}

