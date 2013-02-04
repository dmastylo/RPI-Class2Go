from c2g.models import *
from courses.reports.generation.C2GReportWriter import *
from courses.reports.generation.get_quiz_data import *
import math
import json

mean = lambda k: sum(k)/len(k)

def gen_course_quizzes_report(ready_course, save_to_s3=False):
    
    ### 1- Compose the report file name and instantiate the report writer object
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s-Course-Quizzes.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix)
    s3_filepath = "%s/%s/reports/course_quizzes/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    ### 2- Write the Report Title
    rw.write(content = ["Course Quiz Summaries for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    
    ### 3- Write problem set reports
    rw.write(content = ["Problem sets"], nl = 1)
    
    problemsets = ProblemSet.objects.getByCourse(course=ready_course).order_by('section__index', 'index')
    for q in problemsets:
        WriteQuizSummaryReportContent(q, rw, full=False)
    
    ### 4- Write video reports
    rw.write(content = ["Videos"], nl = 1)
    
    videos = Video.objects.getByCourse(course=ready_course).order_by('section__index', 'index')
    for q in videos:
        WriteQuizSummaryReportContent(q, rw, full=False)
    
    
    ### 5- Proceed to write out and return
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}

def gen_quiz_summary_report(ready_course, ready_quiz, save_to_s3=False):
    
    ### 1- Create the S3 file name and report writer object
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    is_video = isinstance(ready_quiz, Video)
    is_summative = (not is_video) and (ready_quiz.assessment_type == 'assessive')
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, ready_quiz.slug)
    if is_video:
        s3_filepath = "%s/%s/reports/videos_summary/%s" % (course_prefix, course_suffix, report_name)
    else:
        s3_filepath = "%s/%s/reports/problemsets_summary/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    ### 2- Get the quiz data
    quiz_data = get_quiz_data(ready_quiz)
    per_student_data = quiz_data['per_student_data']
    exercise_summaries = quiz_data['exercise_summaries']
    
    ### 4- Write out the report content
    WriteQuizSummaryReportContent(ready_quiz, rw, full=False)

    ### 5- Proceed to write out and return
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}


def gen_course_assessments_report(ready_course, save_to_s3=False):
    
    ### 1- Compose the report file name and instantiate the report writer object
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s-Course-Assessments.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix)
    s3_filepath = "%s/%s/reports/course_assessments/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    ### 2- Write the Report Title
    rw.write(content = ["Course Assessment Summaries for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    
    ### 3- Write problem set reports
    rw.write(content = ["Assessments"], nl = 1)
    
    exams = Exam.objects.getByCourse(course=ready_course).order_by('section__index', 'index')
    for exam in exams:
        WriteAssessmentSummaryReportContent(exam, rw, full=False)
    
    ### 4- Proceed to write out and return
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}

def gen_assessment_summary_report(ready_course, exam, save_to_s3=False):
    
    ### 1- Compose the report file name and instantiate the report writer object
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, exam.slug)
    s3_filepath = "%s/%s/reports/problemsets_summary/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    ### 2- Write the Report Title
    rw.write(content = ["Assessment Summary for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    
    ### 3- Write problem set reports
    WriteAssessmentSummaryReportContent(exam, rw, full=False)
    
    ### 4- Proceed to write out and return
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}

def gen_survey_summary_report(ready_course, survey, save_to_s3=False):
    
    ### 1- Compose the report file name and instantiate the report writer object
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, survey.slug)
    s3_filepath = "%s/%s/reports/survey_summary/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    ### 2- Write the Report Title
    rw.write(content = ["Survey Summary for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    
    ### 3- Write survey report
    WriteSurveySummaryReportContent(survey, rw, full=False)
    
    ### 4- Proceed to write out and return
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}

def gen_assessment_student_scores_report(ready_course, save_to_s3=False):
    
    ### 1- Compose the report file name and instantiate the report writer object
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    s3_filepath = "%s/%s/reports/assessment_student_scores/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    ### 2- Write the Report Title
    rw.write(content = ["Student Scores for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    rw.write(content= ["All student scores shown are with all penalties included"])
    
    ### 3- Write survey report
    WriteAssessmentStudentScoresReportContent(ready_course, rw, full=False)
    
    ### 4- Proceed to write out and return
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}

def WriteQuizSummaryReportContent(ready_quiz, rw, full=False):
    ### 1- Get the quiz data
    quiz_data = get_quiz_data(ready_quiz)
    quiz_summary = quiz_data['quiz_summary']
    exercise_summaries = quiz_data['exercise_summaries']
    
    ### 2- Write the title line
    rw.write([quiz_summary['title']])
    
    ### 3- Write out per-exercise report content
    if len(exercise_summaries) == 0:
        rw.write(content = ["No exercises have been added yet."], indent = 1, nl = 1)
        return
    
    # Summative problem sets get their mean and max scores written in the report
    if quiz_summary['assessment_type'] == 'summative':
        if len(quiz_summary['scores']) > 0:
            rw.write([
                "Mean score", mean(quiz_summary['scores']),
                "Max score", max(quiz_summary['scores']),
                "",
                "Mean score after late penalty", mean(quiz_summary['scores_after_late_penalty']),
                "Max score after late penalty", max(quiz_summary['scores_after_late_penalty']),
            ], indent = 1, nl = 1)
        
    # Exercise summary table header
    content = ["Exercise"]
    if quiz_summary['assessment_type'] == 'summative': content.extend(["Mean score", "Max score"])
    content.extend([
        "Total attempts",
        "Students who have attempted",
        "Correct attempts",
        "Correct 1st attempts",
        "Correct 2nd attempts",
        "Correct 3rd attempts",
        "Median attempts to (and including) first correct attempt",
        "Median attempt time",
        "Most freq incorrect answer",
    ])
    rw.write(content, indent = 1)
    
    # Exercise summary table rows
    for ex_summary in exercise_summaries:
        content = [ex_summary['slug']]
        if quiz_summary['assessment_type'] == 'summative':
            if len(ex_summary['scores']) > 0:
                content.extend([mean(ex_summary['scores']), max(ex_summary['scores'])])
            else:
                content.extend(["", ""])
        
        most_freq_inc_ans_str = "Too few, or no high freq, incorrect attempts"
        if len(ex_summary['most_frequent_incorrect_answers']) > 0:
            most_freq_inc_ans_content = ex_summary['most_frequent_incorrect_answers'][0][0]
            most_freq_inc_ans_percent = ex_summary['most_frequent_incorrect_answers'][0][1]
            most_freq_inc_ans_str = "%s (%.2f%% of all incorrect attempts)" % (most_freq_inc_ans_content, most_freq_inc_ans_percent)
            
        content.extend([
            ex_summary['num_attempts'],
            ex_summary['num_attempting_students'],
            ex_summary['num_correct_attempts'],
            ex_summary['num_correct_first_attempts'],
            ex_summary['num_correct_second_attempts'],
            ex_summary['num_correct_third_attempts'],
            ex_summary['median_num_attempts_to_fca'],
            ex_summary['median_attempt_time'],
            json.dumps(most_freq_inc_ans_str),
        ])
        
        rw.write(content, indent = 1)
        
    rw.write([""])
    
def WriteAssessmentSummaryReportContent(ready_exam, rw, full=False):
    ### 1- Get the assessment data
    exam_summary = get_assessment_data(ready_exam)
    
    ### 2- Write the title line
    rw.write([exam_summary['title']])

    # Field summary table header
    content = ["Field"]
    if exam_summary['assessment_type'] == 'summative': content.extend(["Mean score", "Max score"])
    content.extend([
        "Total attempts",
        "Students who have attempted",
        "Correct attempts",
        "Correct 1st attempts",
        "Correct 2nd attempts",
        "Correct 3rd attempts",
    ])
    rw.write(content, indent = 1, nl=1)

    content = []
    # Fill in the values
    for key, value in exam_summary['total_attempts'].iteritems():
        field_name = exam_summary['human_field'].get(key)
        if not field_name:
            field_name = key

        content.extend([field_name])
        
        if exam_summary['assessment_type'] == 'summative':
            content.extend([
                exam_summary['mean_score'].get(key, 0),
                exam_summary['max_score'].get(key, 0),
                ])
        
        content.extend([
            value,
            exam_summary['distinct_students'].get(key, 0),
            exam_summary['correct_attempts'].get(key,0),
            exam_summary['correct_first_attempts'].get(key, 0),
            exam_summary['correct_second_attempts'].get(key, 0),
            exam_summary['correct_third_attempts'].get(key, 0),
        ])
        rw.write(content, indent = 1)
        content = []
        
    rw.write(content, indent = 1)
        
    rw.write([""])


def WriteSurveySummaryReportContent(ready_survey, rw, full=False):
    
    ### 1- Get the survey data
    tally, errors, question_reports = get_survey_data(ready_survey)
    
    ### 2- Write the title line
    rw.write([ready_survey.title])
    
    ### 3- Write the content
    for question, responses in tally.iteritems():
        
        if question_reports and (question in question_reports):
            content = ["question: " + question, question_reports[question]]
        else:
            content = ["question: " + question]
        
        rw.write(content)
        for response, count in responses.iteritems():
            if response != '+total+':
                content = [response, count]
                rw.write(content, indent = 1)
        content = []
        content = ['Total', "", str(responses['+total+'])]
        rw.write(content, nl = 1)
        
    content = []
    content = [str(errors) + " errors found in parsing the data"]
    rw.write(content)
    rw.write([""])
    
def WriteAssessmentStudentScoresReportContent(ready_course, rw, full=False):
    
    ### 1- Get the exams, excluding surveys, and student score data
    exams, student_scores = get_student_scores(ready_course)
    
    ### 2- Construct scores dictionary
    scores_dict = construct_scores_dict(student_scores)
    
    ### 3- Construct column title array and max_scores array and print them.
    titles = ["", "Title"]
    max_scores = ["", "Max Score"]
    for exam in exams:
        titles += [exam['title']]
        max_scores += [exam['total_score']]
    rw.write(titles)
    rw.write(max_scores)
    rw.write([""])
    
    ### 4- Print the sorted scores_dict matching exam titles as we go.
    row = []
    for username, scores in sorted(scores_dict.iteritems()):
        row += [username]
        row += [scores['name']]
        for title in titles:
            if scores.get(title, False):
                row += [str(scores.get(title))]
            elif titles.index(title) not in [0, 1]:
                row += [""]
            
        rw.write(row)
        row = []  
        
    rw.write([""])
    
def construct_scores_dict(student_scores):
    # scores_dict is a dict of dicts. Each dict represents a row in the report for a
    # username. All this block does is convert rows from the returned queryset into
    # columns for the report.
    # Each dict contains <exam title>:<score> key:value pairs.
    scores_dict = {}
    last_username = ""
    for student_score in student_scores:
        username = student_score['student__username']
        if username != last_username:
            scores_dict[username] = {}
            scores_dict[username]['username'] = username
            scores_dict[username]['name'] = student_score['student__first_name'] + " " + student_score['student__last_name']
        
        scores_dict[username][student_score['exam__title']] = student_score['score']
        last_username = username
        
    return scores_dict
