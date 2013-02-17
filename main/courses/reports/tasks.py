import logging
from celery import task
from courses.reports.generation.gen_course_dashboard_report import *
from courses.reports.generation.gen_quiz_summary_report import *
from courses.reports.generation.gen_quiz_full_report import *
from courses.reports.generation.gen_class_roster import *

from django.core.mail import EmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)

@task
@use_readonly_database
def generate_and_email_reports(username, course_handle, requested_reports, email_title, email_message, attach_reports_to_email = True):
    # Generates the list of reports in requested_reports, and sends it to the staff of the given course.
    ready_course = Course.objects.get(handle=course_handle, mode='ready')
    
    # Generate requested reports
    reports = []
    for rr in requested_reports:
        if rr['type'] == 'dashboard':
            logger.info("User %s requested to generate dashboard report for course %s." % (username, course_handle))
            report = gen_course_dashboard_report(ready_course, save_to_s3=True)
            report['type'] = rr['type']
            if report:
                reports.append(report)
                logger.info("Dashboard report for course %s generated successfully for user %s." % (course_handle, username))
            else:
                logger.info("Failed to generate dashboard report for course %s for user %s." % (course_handle, username))
            
        elif rr['type'] == 'video_full':
            if (not 'slug' in rr) or (not rr['slug']):
                logger.info("Missing slug -- Failed to generate video full report")
            else:
                slug = rr['slug']
                logger.info("User %s requested to generate video full report for course %s video slug %s." % (username, course_handle, slug))
                # If instructors ask for a report for a quiz that doesn't have a live instance, pass the draft instance instead. The report generators will handle this special case
                try:
                    quiz = Video.objects.get(course=ready_course, slug=slug)
                except Video.DoesNotExist:
                    quiz = Video.objects.get(course=ready_course.image, slug=slug)
                    
                report = gen_quiz_full_report(ready_course, quiz, save_to_s3=True)
                report['type'] = rr['type']
                if report:
                    reports.append(report)
                    logger.info("Video full report for course %s video %s generated successfully for user %s." % (course_handle, slug, username))
                else:
                    logger.info("Failed to generate video full report for course %s video %s for user %s." % (course_handle, slug, username))
                    
        elif rr['type'] == 'video_summary':
            if (not 'slug' in rr) or (not rr['slug']):
                logger.info("Missing slug -- Failed to generate video report")
            else:
                slug = rr['slug']
                logger.info("User %s requested to generate video summary report for course %s video slug %s." % (username, course_handle, slug))
                # If instructors ask for a report for a quiz that doesn't have a live instance, pass the draft instance instead. The report generators will handle this special case
                try:
                    quiz = Video.objects.get(course=ready_course, slug=slug)
                except Video.DoesNotExist:
                    quiz = Video.objects.get(course=ready_course.image, slug=slug)
                    
                report = gen_quiz_summary_report(ready_course, quiz, save_to_s3=True)
                report['type'] = rr['type']
                if report:
                    reports.append(report)
                    logger.info("Video summary report for course %s video %s generated successfully for user %s." % (course_handle, slug, username))
                else:
                    logger.info("Failed to generate video summary report for course %s video %s for user %s." % (course_handle, slug, username))
                    
        elif rr['type'] == 'class_roster':
            logger.info("User %s requested to generate class roster for course %s." % (username, course_handle))
            report = gen_class_roster(ready_course, save_to_s3=True)
            report['type'] = rr['type']
            if report:
                reports.append(report)
                logger.info("Class roster for course %s generated successfully for user %s." % (course_handle, username))
            else:
                logger.info("Failed to generate class roster for course %s for user %s." % (course_handle, username))
                    
        elif rr['type'] == 'course_assessments':
            logger.info("User %s requested to generate course assessments report for course %s." % (username, course_handle))
            report = gen_course_assessments_report(ready_course, save_to_s3=True)
            report['type'] = rr['type']
            if report:
                reports.append(report)
                logger.info("Course assessments report for course %s generated successfully for user %s." % (course_handle, username))
            else:
                logger.info("Failed to generate course assessments report for course %s for user %s." % (course_handle, username))
                
        elif rr['type'] == 'assessment_full':
            if (not 'slug' in rr) or (not rr['slug']):
                logger.info("Missing slug -- Failed to generate assessment full report")
            else:
                slug = rr['slug']
                logger.info("User %s requested to generate assessment full report for course %s assessment slug %s." % (username, course_handle, slug))
                
                # If instructors ask for a report for an exam that doesn't have a live instance, pass the draft instance instead. The report generators will handle this special case
                try:
                    exam = Exam.objects.get(course=ready_course, slug=slug)
                except Exam.DoesNotExist:
                    exam = Exam.objects.get(course=ready_course.image, slug=slug)
                    
                report = gen_assessment_full_report(ready_course, exam, save_to_s3=True)
                report['type'] = rr['type']
                if report:
                    reports.append(report)
                    logger.info("Assessment full report for course %s assessment %s generated successfully for user %s." % (course_handle, slug, username))
                else:
                    logger.info("Failed to generate assessment full report for course %s assessment %s for user %s." % (course_handle, slug, username))
                    
        elif rr['type'] == 'assessment_summary':
            if (not 'slug' in rr) or (not rr['slug']):
                logger.info("Missing slug -- Failed to generate assessment summary report")
            else:
                slug = rr['slug']
                logger.info("User %s requested to generate assessment summary report for course %s assessment slug %s." % (username, course_handle, slug))
                
                # If instructors ask for a report for a quiz that doesn't have a live instance, pass the draft instance instead. The report generators will handle this special case
                try:
                    exam = Exam.objects.get(course=ready_course, slug=slug)
                except Exam.DoesNotExist:
                    exam = Exam.objects.get(course=ready_course.image, slug=slug)
                    
                report = gen_assessment_summary_report(ready_course, exam, save_to_s3=True)
                report['type'] = rr['type']
                if report:
                    reports.append(report)
                    logger.info("Assessment summary report for course %s assessment %s generated successfully for user %s." % (course_handle, slug, username))
                else:
                    logger.info("Failed to generate assessment summary report for course %s assessment %s for user %s." % (course_handle, slug, username))
                            

        elif rr['type'] == 'survey_summary':
            if (not 'slug' in rr) or (not rr['slug']):
                logger.info("Missing slug -- Failed to generate survey summary report")
            else:
                slug = rr['slug']
                logger.info("User %s requested to generate survey summary report for course %s survey slug %s." % (username, course_handle, slug))
                
                # If instructors ask for a report for a survey that doesn't have a live instance, pass the draft instance instead. The report generators will handle this special case
                try:
                    survey = Exam.objects.get(course=ready_course, slug=slug)
                except Exam.DoesNotExist:
                    survey = Exam.objects.get(course=ready_course.image, slug=slug)
                    
                report = gen_survey_summary_report(ready_course, survey, save_to_s3=True)
                report['type'] = rr['type']
                
                reports.append(report)
                logger.info("Survey summary report for course %s assessment %s generated successfully for user %s." % (course_handle, slug, username))
            
            
        elif rr['type'] == 'assessment_student_scores':
            logger.info("User %s requested to generate assessment student scores report for course %s." % (username, course_handle))
            report = gen_assessment_student_scores_report(ready_course, save_to_s3=True)
            report['type'] = rr['type']
            
            reports.append(report)
            logger.info("Assessment student scores report for course %s generated successfully for user %s." % (course_handle, username))            
            
    send_emails = getattr(settings, 'EMAIL_NIGHTLY_REPORTS', False)
    if send_emails:
        # Email Generated Reports
        staff_email = ready_course.contact
        if not staff_email:
            logger.info("Failed to email reports for course %s -- Missing course contact email" % (course_handle))
        else:
            if len(reports) == 0:
                logger.info("Not sending reports email to %s, because no reports were generated." % staff_email)
                return
                
            email = EmailMessage(
                email_title,             # Title
                email_message,           # Message
                settings.SERVER_EMAIL,   # From
                [staff_email, ],         # To
            )
            if attach_reports_to_email:
                for report in reports:
                    if report['type'] in ['problemset_summary', 'video_summary']:
                        report_name = report['name'][:-4] + '_summary.csv'
                    else:
                        report_name = report['name']
                        
                    email.attach(report_name, report['content'], 'text/csv')
                
            email.send()
        
