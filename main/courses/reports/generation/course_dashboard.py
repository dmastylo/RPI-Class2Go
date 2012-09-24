from c2g.models import *
from django.contrib.auth.models import User,Group
from courses.reports.data_aggregation.course_dashboard import *
from datetime import datetime, timedelta
import csv
from database import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
from django.core.files.storage import default_storage
from storages.backends.s3boto import S3BotoStorage

def gen_course_dashboard_report(course, save_to_s3=False):
        dd = get_course_dashboard_report_data(course)
        
        ### Output ###
        secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
                
        csv_rows = []
        txt_string = ""
        
        # Title
        txt_string += "Dashboard for %s (%s %d)\n" % (course.title, course.term.title(), course.year)
        txt_string += "----------------------------------------------------------\n\n"
        
        csv_rows.append(["Dashboard for %s (%s %d)" % (course.title, course.term.title(), course.year)])
        csv_rows.append([])
        
        # Members
        txt_string += "\tCourse Members\n"
        txt_string += "\t--------------\n"
        txt_string += "\t\t%d professors, %d TAs, %d read-only TAs, and %d students\n\n" % (dd['num_instructors'], dd['num_tas'], dd['num_readonly_tas'], dd['num_students'])
        
        csv_rows.append(["Course Members"])
        csv_rows.append(["", "Students", dd['num_students'], "Professors", dd['num_instructors'], "TAs", dd['num_tas'], "Readonly TAs", dd['num_readonly_tas']])
        csv_rows.append([])
        
        # Content
        txt_string += "\tCourse Content\n"
        txt_string += "\t--------------\n"
        txt_string += "\t\tProblem sets: %d (%d live)\n" % (dd['ps']['num'], dd['ps']['num_live'])
        txt_string += "\t\t\tFormative: %d (%d live)\t-\tSummative: %d (%d live)\n" % (dd['ps']['num_formative'], dd['ps']['num_formative_live'], dd['ps']['num_summative'], dd['ps']['num_summative_live'])
        txt_string += "\t\tVideos: %d (%d live)\n" % (dd['vd']['num'], dd['vd']['num_live'])
        txt_string += "\t\tAdditional pages: %d (%d live)\n" % (dd['ap']['num'], dd['ap']['num_live'])
        txt_string += "\t\tFiles: %d (%d live)\n\n" % (dd['fl']['num'], dd['fl']['num_live'])
        
        csv_rows.append(["Course Content"])
        csv_rows.append(["", "Problem sets", "Total", dd['ps']['num'], "Live", dd['ps']['num_live']])
        csv_rows.append(["", "", "Formative", "Total", dd['ps']['num_formative'], "Live", dd['ps']['num_formative_live']])
        csv_rows.append(["", "", "Summative", "Total", dd['ps']['num_summative'], "Live", dd['ps']['num_summative_live']])
        csv_rows.append(["", "Videos", "Total", dd['vd']['num'], "Live", dd['vd']['num_live']])
        csv_rows.append(["", "Additional Pages", "Total", dd['ap']['num'], "Live", dd['ap']['num_live']])
        csv_rows.append(["", "Files", "Total", dd['fl']['num'], "Live", dd['fl']['num_live']])
        csv_rows.append([])
        
        # Activity
        txt_string += "\tCourse Activity (Only Live Course Content is Displayed)\n"
        txt_string += "\t--------------------------------------------------------\n\n"
        
        csv_rows.append(["Course Activity (Only Live Course Content is Displayed)"])
        csv_rows.append([])
        
        txt_string += "\tVisits to Problem sets, Videos, Additional Pages, and the Forum\n"
        txt_string += "\t---------------------------------------------------------------\n"
        txt_string += "\t\tAdditional pages: %d total, %d unique \n\t\tForum: %d total, %d unique \n\t\tProblem sets: %d total, %d unique \n\t\tVideos: %d total, %d unique\n\n" % (dd['ap']['aggr_visits']['total'], dd['ap']['aggr_visits']['unique'], dd['fm']['visits']['total']['all_time'], dd['fm']['visits']['unique']['all_time'], dd['ps']['aggr_visits']['total'], dd['ps']['aggr_visits']['unique'], dd['vd']['aggr_visits']['total'], dd['vd']['aggr_visits']['unique'])
        
        csv_rows.append(["Visits to Problem sets, Videos, Additional Pages, and the Forum"])
        csv_rows.append(["", "Additional pages", "Total", dd['ap']['aggr_visits']['total'], "Unique", dd['ap']['aggr_visits']['unique']])
        csv_rows.append(["", "Forum", "Total", dd['fm']['visits']['total']['all_time'], "Unique", dd['fm']['visits']['unique']['all_time']])
        csv_rows.append(["", "Problem sets", "Total", dd['ps']['aggr_visits']['total'], "Unique", dd['ps']['aggr_visits']['unique']])
        csv_rows.append(["", "Videos", "Total", dd['vd']['aggr_visits']['total'], "Unique", dd['vd']['aggr_visits']['unique']])
        csv_rows.append([])
        
        txt_string += "\tDetails\n"
        txt_string += "\t-------\n"
        
        csv_rows.append(["", "Details"])
        csv_rows.append([])
        
        # Problem Sets
        txt_string += "\t\tProblem Sets\n"
        txt_string += "\t\t------------\n"
        if len(dd['ps']['list']) == 0: txt_string += "\t\tNo live problem sets exist at the moment\n"
        else: txt_string += gen_item_list_visits("\t\t", dd['ps']['list'])
        txt_string += "\n"
        
        csv_rows.append(["", "", "Problem Sets"])
        csv_rows.append([])
        if len(dd['ps']['list']) == 0:
            csv_rows.append(["", "", "\t\tNo live problem sets exist yet"])
            csv_rows.append([])
        for item in dd['ps']['list']:
            csv_rows.append(["", "", "", item['object'].title])
            csv_rows.append(["", "", "", "", "", "Total", "Unique"])
            csv_rows.append(["", "", "", "", "Past 24 hours", item['visits']['total']['past_24_hours'], item['visits']['unique']['past_24_hours']])
            csv_rows.append(["", "", "", "", "Past Week", item['visits']['total']['past_week'], item['visits']['unique']['past_week']])
            csv_rows.append(["", "", "", "", "All time", item['visits']['total']['all_time'], item['visits']['unique']['all_time']])
            csv_rows.append([])
        
        # Videos
        txt_string += "\t\tVideos\n"
        txt_string += "\t\t------\n"
        if len(dd['vd']['list']) == 0: txt_string += "\t\tNo live videos exist at the moment\n"
        else: txt_string += gen_item_list_visits("\t\t", dd['vd']['list'])
        txt_string += "\n"
        
        csv_rows.append(["", "", "Videos"])
        csv_rows.append([])
        if len(dd['vd']['list']) == 0:
            csv_rows.append(["", "", "No live videos exist yet"])
            csv_rows.append([])
        for item in dd['vd']['list']:
            csv_rows.append(["", "", "", item['object'].title])
            csv_rows.append(["", "", "", "", "", "Total", "Unique"])
            csv_rows.append(["", "", "", "", "Past 24 hours", item['visits']['total']['past_24_hours'], item['visits']['unique']['past_24_hours']])
            csv_rows.append(["", "", "", "", "Past Week", item['visits']['total']['past_week'], item['visits']['unique']['past_week']])
            csv_rows.append(["", "", "", "", "All time", item['visits']['total']['all_time'], item['visits']['unique']['all_time']])
            csv_rows.append([])
        
        # Additional Pages
        txt_string += "\t\tAdditional Pages\n"
        txt_string += "\t\t----------------\n"
        if len(dd['ap']['list']) == 0: txt_string += "No live additional pages exist at the moment\n"
        else: txt_string += gen_item_list_visits("\t\t", dd['ap']['list'])
        txt_string += "\n"
        
        csv_rows.append(["", "", "Additional Pages"])
        csv_rows.append([])
        if len(dd['ap']['list']) == 0:
            csv_rows.append(["", "", "No live additional pages exist yet"])
            csv_rows.append([])
        for item in dd['ap']['list']:
            csv_rows.append(["", "", "", item['object'].title])
            csv_rows.append(["", "", "", "", "", "Total", "Unique"])
            csv_rows.append(["", "", "", "", "Past 24 hours", item['visits']['total']['past_24_hours'], item['visits']['unique']['past_24_hours']])
            csv_rows.append(["", "", "", "", "Past Week", item['visits']['total']['past_week'], item['visits']['unique']['past_week']])
            csv_rows.append(["", "", "", "", "All time", item['visits']['total']['all_time'], item['visits']['unique']['all_time']])
            csv_rows.append([])
        
        # Forum
        txt_string += "\t\tForum\n"
        txt_string += "\t\t----------------\n"
        txt_string += gen_visit_table("\t\t", dd['fm']['visits'], recent=True)
        txt_string += "\n"
        
        csv_rows.append(["", "", "Forum"])
        csv_rows.append([ "", "", "", "Total", "Unique"])
        csv_rows.append([ "", "", "Past 24 hours", dd['fm']['visits']['total']['past_24_hours'], dd['fm']['visits']['unique']['past_24_hours']])
        csv_rows.append([ "", "", "Past Week", dd['fm']['visits']['total']['past_week'], dd['fm']['visits']['unique']['past_week']])
        csv_rows.append([ "", "", "All time", dd['fm']['visits']['total']['all_time'], dd['fm']['visits']['unique']['all_time']])
        csv_rows.append([])
        
        # Write Out the files
        if save_to_s3:
            dt = datetime.now()
            csv_file = secure_file_storage.open("%s/%s/reports/dashboard/csv/%02d_%02d_%02d__%02d_%02d_%02d-%s-Dashboard.csv" % (course.handle.split('--')[0], course.handle.split('--')[1], dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course.handle.split('--')[0]+"_"+course.handle.split('--')[1]), 'wb')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(csv_rows)
            csv_file.close()
            
            txt_file = secure_file_storage.open("%s/%s/reports/dashboard/txt/%02d_%02d_%02d__%02d_%02d_%02d-%s-Dashboard.txt" % (course.handle.split('--')[0], course.handle.split('--')[1], dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course.handle.split('--')[0]+"_"+course.handle.split('--')[1]), 'wb')
            txt_file.write(txt_string)
            txt_file.close()
            
        return txt_string
        

def gen_item_list_visits(tabs, items):
    str = ""
    
    recent_items = []
    older_items = []
    
    for item in items:
        if item['object'].live_datetime and (item['object'].live_datetime > datetime.now() - timedelta(days=14)): recent_items.append(item)
        else: older_items.append(item)
    
    str += "%sRecent (Live within past 2 weeks):\n" % tabs
    str += "%s----------------------------------\n" % tabs
    if len(recent_items) > 0:
        for item in recent_items:
            str += tabs+" * "+item['object'].title + "\n"
            str += gen_visit_table(tabs+"\t", item['visits'], recent=True)
            
    else:
        str += tabs+"\tNone\n"
        
    str += "%sOlder:\n" % tabs
    str += "%s------\n" % tabs
    if len(older_items) > 0:
        for item in older_items:
            str += tabs+" * "+item['object'].title + "\n"
            str += gen_visit_table(tabs+"\t", item['visits'], recent=False)
            
    else:
        str += tabs+"\tNone\n"
        
    return str
        
    
def gen_visit_table(tabs, visits, recent=True):
    addl_tab = "\t\t"
    
    str  = "%s\t\tTotal visits\t\tUnique visits\n" % (addl_tab+tabs)
    str += "%s\t\t------------\t\t-------------\n\n" % (addl_tab+tabs)
    if recent:
        str += "%s Past 24 hours:\t%d\t\t\t\t\t%d\n" % (tabs, visits['total']['past_24_hours'], visits['unique']['past_24_hours'])
        str += "%s Past Week:\t\t%d\t\t\t\t\t%d\n" % (tabs, visits['total']['past_week'], visits['unique']['past_week'])
    str += "%s All time:\t\t%d\t\t\t\t\t%d\n\n" % (tabs, visits['total']['all_time'], visits['unique']['all_time'])
    
    return str
 