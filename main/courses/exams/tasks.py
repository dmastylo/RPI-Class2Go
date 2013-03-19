from celery import task
from c2g.models import ExamRecord, Course, Exam
from django.core.mail import EmailMessage, get_connection
from django.core.mail import send_mail
from storages.backends.s3boto import S3BotoStorage

import json
import settings
import datetime

FILE_DIR = getattr(settings, 'FILE_UPLOAD_TEMP_DIR', '/tmp')
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
AWS_SECURE_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_SECURE_STORAGE_BUCKET_NAME', '')

@task()
def generate_submission_csv_task(course_id, exam_id, email_to):
    
    course = Course.objects.get(id=course_id)
    exam = Exam.objects.get(id=exam_id)
    
    course_prefix = course.prefix
    course_suffix = course.suffix
    exam_slug = exam.slug
    
    submitters = ExamRecord.objects.filter(exam=exam, complete=True, time_created__lt=exam.grace_period).values('student').distinct()
    fname = course_prefix+"-"+course_suffix+"-"+exam_slug+"-"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".csv"
    outfile = open(FILE_DIR+"/"+fname,"w+")
    
    could_not_parse = ""
    
    for s in submitters: #yes, there is sql in a loop here.  We'll optimize later
        latest_sub = ExamRecord.objects.values('student__username', 'time_created', 'json_data').filter(exam=exam, time_created__lt=exam.grace_period, student=s['student']).latest('time_created')
        try:
            sub_obj = json.loads(latest_sub['json_data']).iteritems()
            for k,v in sub_obj:
                vals = parse_val(v)
                outstring = '"%s","%s","%s"\n' % (latest_sub['student__username'], k, vals)
                outfile.write(outstring)
        except ValueError:
            could_not_parse += latest_sub['student__username']+ " " #Don't output if the latest submission was erroneous
    
    outfile.write("\n")
    
    #if there were items we could not parse
    if could_not_parse:
        #write the usernames at the beginning of the file
        outfile.seek(0)
        data=outfile.read()
        outfile.seek(0)
        outfile.truncate()
        outfile.write("Could not parse data from the following users: " + could_not_parse + "\n")
        outfile.write(data)
    
    #write to S3
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    s3file = secure_file_storage.open("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname),'w')
    try:
        outfile.seek(0)
        s3file.write(outfile.read())
    finally:
        s3file.close()
        outfile.close()

    dl_url = secure_file_storage.url_monkeypatched("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname), response_headers={'response-content-disposition': 'attachment'})

    email = EmailMessage('%s: Submission CSV for %s' % (course.title, exam.title), "The student submissions CSV for %s is ready.  Because the file can be large, please download it at %s." % (exam.title, dl_url),
                         settings.SERVER_EMAIL,
                         [email_to])
    email.send()


def parse_val(v):
    """Helper function to parse AJAX submissions"""
    if isinstance(v,list):
        sorted_list = sorted(map(lambda li: li['value'], v))
        return reduce(lambda x,y: x+y+",", sorted_list, "")
    else:
        try:
            return v.get('value', "")
        except (TypeError, AttributeError):
            return str(v)

    