from c2g.models import *
from courses.reports.data_aggregation.course_quizzes import *
import csv
from database import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SECURE_STORAGE_BUCKET_NAME
from django.core.files.storage import default_storage
from storages.backends.s3boto import S3BotoStorage

def gen_course_quizzes_report(course, save_to_s3=False):
    qd = get_course_quizzes_report_data(course)
        
    ### Output ###
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    
    csv_rows = []
    txt_string = ""
    
    # Txt quizzes are listed under one another
    txt_string += "Quizzes Report for %s (%s %d)\n" % (course.title, course.term.title(), course.year)
    txt_string += "--------------------------------------------------------------------\n\n"
    tmp_str = ""
    for quiz_data in qd: tmp_str += gen_quiz_report_string(quiz_data) + "\n"
    if len(tmp_str) == 0: tmp_str = "No live quizzes exist at the moment\n"
    txt_string += tmp_str

    
    csv_rows.append(["Quizzes Report for %s (%s %d)" % (course.title, course.term.title(), course.year)])
    csv_rows.append([])
    
    temp_rows = []
    for quiz_data in qd:temp_rows.extend(gen_quiz_rows(quiz_data))
    if len(temp_rows) == 0:
        temp_rows = [["No live quizzes exist at the moment"]]
    csv_rows.extend(temp_rows)
    
    # Write Out the files
    if save_to_s3:
        dt = datetime.now()
        csv_file = secure_file_storage.open("%s/%s/reports/course_quizzes/csv/%02d_%02d_%02d__%02d_%02d_%02d-%s-Quizzes.csv" % (course.handle.split('--')[0], course.handle.split('--')[1], dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course.handle.split('--')[0]+"_"+course.handle.split('--')[1]), 'wb')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_rows)
        csv_file.close()
        
        txt_file = secure_file_storage.open("%s/%s/reports/course_quizzes/txt/%02d_%02d_%02d__%02d_%02d_%02d-%s-Quizzes.txt" % (course.handle.split('--')[0], course.handle.split('--')[1], dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course.handle.split('--')[0]+"_"+course.handle.split('--')[1]), 'wb')
        txt_file.write(txt_string)
        txt_file.close()
        
    return txt_string
        
       
def gen_quiz_report_string(qd):
    if isinstance(qd['quiz'], Video):
        type_ = 'video'
        if len(qd['exercises']) == 0:
            return ''
    else:
        if qd['quiz'].assessment_type == 'summative': type_ = 'summative problem set'
        else: type_ = 'formative problem set'
    
    str_  = ''
    str_ += '%s (%s)\n' % (qd['quiz'].title, type_.title())
    str_ += '-' * len(str_) + "\n"
    
    if len(qd['exercises']) == 0:
        str_ += "No exercises have been added yet to this %s\n" % type_
        return str_
        
    if not qd['has_attempts']:
        str_ += "No attempts yet for this %s" % type_
        return str_
    
    if type_ == 'summative problem set':
        str_ += "Mean score: %s\t Max score: %s\n" % (str(qd['mean_score']), str(qd['max_score']))
    
    for exercise in qd['exercises']:
        str_ += gen_exercise_report_string(exercise)
        
    return str_
       
def gen_exercise_report_string(ed):
    str_ = ""
    str_ += "\t" + ed['exercise'].get_slug() + "\n"
    str_ += "\t" + '-' * len(ed['exercise'].get_slug()) + "\n"
    
    if not ed['has_attempts']:
        str_ += "\t\tNo attempts yet for this exercise\n"
        return str

    str_ += "\t\tTotal number of attempts: %d (avg %.2f per student)\n" % (ed['num_attempts'], 1.0*ed['num_attempts']/ed['num_unique_attempts'])        
    str_ += "\t\tMean time per attempt: %d seconds\n" % ed['mean_time_per_attempt']
    if 'max_score' in ed: str_ += "\t\tMean score: %d \t Max score: %d\n" % (ed['mean_score'], ed['max_score'])
    str_ += "\t\tStudents with attempts: %d \t Students with correct attempts: %d (%d percent)\n" % (ed['num_unique_attempts'], ed['num_students_with_correct_attempt'], int(100*ed['num_students_with_correct_attempt']/ed['num_unique_attempts']))
    str_ += "\t\tStudents with correct:\t1st attempts: %.1f percent\t2nd attempts:%.1f percent\t3rd attempts:%.1f percent\n" % (100.0*ed['num_students_with_correct_first_attempt']/ed['num_unique_attempts'], 100.0*ed['num_students_with_correct_second_attempt']/ed['num_unique_attempts'], 100.0*ed['num_students_with_correct_third_attempt']/ed['num_unique_attempts'])

    return str_
    
def gen_quiz_rows(qd):
    quiz_rows = []
    is_summative = False
    
    if isinstance(qd['quiz'], Video):
        type_ = 'video'
        if len(qd['exercises']) == 0:
            return [] # Do not show an entry for videos with no exercises
    else:
        if qd['quiz'].assessment_type == 'summative':
            type_ = 'summative problem set'
            is_summative = True
        else: type_ = 'formative problem set'
    
    quiz_rows.append([qd['quiz'].title, '('+type_.title()+')'])
    
    if len(qd['exercises']) == 0:
        # Show the no exercises message for PS with no exercises
        quiz_rows.append(["", "No exercises yet in this %s" % type_])
        return quiz_rows
        
    if not qd['has_attempts']:
        quiz_rows.append(['No attempts yet.'])
        quiz_rows.append([])
        return quiz_rows
        
    if type_ == 'summative problem set':
        quiz_rows.append(["", 'Mean score', qd['mean_score'], 'Max score', qd['max_score']])
    
    quiz_rows.append(['', 'Exercise details'])
    
    ex_header_row = ["", "", "", "Num attempts", "Av attempts per student", "Mean attempt time", ""]
    if is_summative: ex_header_row.extend(["Mean score","Max score", ""])
    ex_header_row.extend(["Stud w/ Attempts", "Stud w/ Correct Attempts", "Stud w/ Correct First Attempts", "Stud w/ Correct Second Attempts", "Stud w/ Correct Third Attempts"])
    
    quiz_rows.append(ex_header_row)
    
    for ed in qd['exercises']:
        ex_row = ["", ed['exercise'].get_slug(), "", ed['num_attempts'], "%.2f" % (1.0*ed['num_attempts']/ed['num_unique_attempts']), ed['mean_time_per_attempt'], ""]
        if is_summative:
            ex_row.extend([ed['mean_score'], ed['max_score'], ""])
        ex_row.extend([ed['num_unique_attempts'], ed['num_students_with_correct_attempt'], ed['num_students_with_correct_first_attempt'], ed['num_students_with_correct_second_attempt'], ed['num_students_with_correct_third_attempt']])
    
        quiz_rows.append(ex_row)
   
    quiz_rows.append([])
    
    return quiz_rows 
