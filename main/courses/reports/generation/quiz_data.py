from c2g.models import *
from courses.reports.data_aggregation.quiz_attempts import *
import csv
from database import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
from django.core.files.storage import default_storage
from storages.backends.s3boto import S3BotoStorage

def gen_quiz_data_report(ready_course, ready_quiz, order_by, save_to_s3=False):
    ex_att_dl = get_quiz_attempts_report_data(ready_quiz, order_by)
    ad = aggregate_quiz_attempts_report_data(ready_quiz, ex_att_dl)
    
    ### Output ###
    is_summative = isinstance(ready_quiz, ProblemSet) and (ready_quiz.assessment_type == 'summative')
    res_table = ad['res_table']
    sorted_usernames = sorted(res_table.keys())
    
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    
    txt_string = ""
    csv_rows = []
    
    # Title
    txt_string += "Quiz Attempts for Quiz \"%s\" in %s (%s %d)\n" % (ready_quiz.title, ready_course.title, ready_course.term.title(), ready_course.year)
    txt_string += "-----------------------------------------------------------------------------------------\n\n"
    
    csv_rows.append(["Quiz Attempts for Quiz \"%s\" in %s (%s %d)" % (ready_quiz.title, ready_course.title, ready_course.term.title(), ready_course.year)]) 
    csv_rows.append([])
    
    # Txt file has exercise listed under each other
    for ex in ad['exercises']:
        
        txt_string += ex.get_slug()+"\n"
        txt_string += "----------------\n"
        
        txt_string += "Username" + (' ' * 17) + "Name" + (' ' * 26) + "Avg Time/Attempt" + ((' ' * 4) + "Score" if is_summative else '') + (' ' * 5) + "Attempts\n"
        txt_string += "--------" + (' ' * 17) + "----" + (' ' * 26) + "----------------" + ((' ' * 4) + "-----" if is_summative else '') + (' ' * 5) + "--------\n"

        for stud_username in sorted_usernames:
            if ex.id in res_table[stud_username]: stud_ex_res = res_table[stud_username][ex.id]
            else:
                stud_ex_res = {'attempts': [], 'mean_attempt_time': '', 'score': ''}
                for e in res_table[stud_username]:
                    stud_ex_res['student'] = res_table[stud_username][e]['student']
                    break
            txt_string += gen_stud_ex_res_string(stud_ex_res['student'], stud_ex_res['mean_attempt_time'], stud_ex_res['score'], stud_ex_res['attempts'], is_summative) + "\n"
            
        txt_string += "\n"
        
        txt_string += "Total Scores for Quiz:\n"
        txt_string += "----------------------\n"
    
    for stud_username in sorted_usernames:
            txt_string += content_pad(stud_username, 20) + "%.1f\n" % ad['totals'][stud_username]
        
        
    # CSV file has exercises listed next to each other
    header_row = ["Username","First name", "Last name"]
    ex_details_row = ["", "", ""]
    for ex in ad['exercises']:
        header_row.extend(["", ex.get_slug(), "", ""])
        ex_details_row.extend(["", "Score", "Mean time", "Attempts"])
    header_row.extend(["", "Total score"])
    
    csv_rows.append(header_row)
    csv_rows.append(ex_details_row)
    
    for stud_username in sorted_usernames:
        for e in res_table[stud_username]:
            student = res_table[stud_username][e]['student']
            break
        
        student_row = [stud_username, student.first_name, student.last_name]
        for ex in ad['exercises']:
            if ex.id in res_table[stud_username]:
                stud_ex_res = res_table[stud_username][ex.id]
                
                attempts = ""
                for i in range(len(stud_ex_res['attempts'])):
                    if i > 0: attempts += ' | '
                    attempts += stud_ex_res['attempts'][i]
                    
                student_row.extend(["", stud_ex_res['score'], stud_ex_res['mean_attempt_time'], attempts])
            else:
                student_row.extend(["", "", "", ""])
                
        student_row.extend(["", ad['totals'][stud_username]])
        csv_rows.append(student_row)
        
    # Write out the files
    if save_to_s3:
        dt = datetime.now()
        csv_file = secure_file_storage.open("%s/%s/reports/quiz_data/csv/%02d_%02d_%02d__%02d_%02d_%02d-%s-Quiz-Data.csv" % (ready_course.handle.split('--')[0], ready_course.handle.split('--')[1], dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, ready_quiz.slug), 'wb')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_rows)
        csv_file.close()
        
        txt_file = secure_file_storage.open("%s/%s/reports/quiz_data/txt/%02d_%02d_%02d__%02d_%02d_%02d-%s-Quiz-Data.txt" % (ready_course.handle.split('--')[0], ready_course.handle.split('--')[1], dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, ready_quiz.slug), 'wb')
        txt_file.write(txt_string)
        txt_file.close()
        
    return txt_string
    
def gen_stud_ex_res_string(student, mean_attempt_time, score, attempts, is_summative):
    str_ = content_pad(student.username, 25) + content_pad(student.first_name + ' ' + student.last_name, 30) + content_pad(mean_attempt_time, 20)
    if is_summative: str_ += content_pad(score, 10)
    
    if len(attempts) > 0:
        for i in range(len(attempts)):
            if i > 0: str_ += ' | '
            str_ += attempts[i]
    else:
        str_ += 'No attempts'
        
    return str_

def content_pad(content, length):
    return content + ((' '*(length-len(content))) if len(content) < length else '')

