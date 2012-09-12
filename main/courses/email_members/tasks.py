from django.core.mail import EmailMultiAlternatives, get_connection
from subprocess import Popen, PIPE, STDOUT
from celery import task
from time import sleep
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from c2g.models import Course, CourseEmail
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site

import math

EMAILS_PER_WORKER=getattr(settings, 'EMAILS_PER_WORKER', 200)

@task()
def delegate_emails(hash_for_msg, total_num_emails):
    '''Delegates emails by spinning up appropriate number of sender workers
    '''
    num_workers=int(math.ceil(float(total_num_emails)/float(EMAILS_PER_WORKER)))
    for i in range(num_workers):
        course_email_with_celery.delay(hash_for_msg,i,num_workers)
    return num_workers

@task()
def course_email_with_celery(hash_for_msg, worker_id=0, num_workers=1):
    """
        Takes a subject and an html formatted email and sends it from sender to all addresses
        in the to_list, with each recipient being the only "to".  Emails are sent multipart, in both
        plain text and html.  Send using celery task.
        
        For work division, this task can be called with num_workers and worker_id, where num_workers is the
        total number of workers and worker_id is the id of this worker, 
        out of a set with ids 0 to num_workers-1, in homage to the fact that python lists are zero based.
    """
    msg = CourseEmail.objects.get(hash=hash_for_msg)
    course = msg.course
    
    p = Popen(['lynx','-stdin','-dump'], stdin=PIPE, stdout=PIPE)
    (plaintext, err_from_stderr) = p.communicate(input=msg.html_message) #use lynx to get plaintext
    course_title=course.title
    from_addr = course.title + ' Staff <class2go-noreply@cs.stanford.edu>'
    
    (course_prefix, delimiter, course_suffix) = course.handle.partition('--')
    site = Site.objects.get(id=1)

    course_url='http://'+site.domain+reverse('courses.views.main', args=[course_prefix, course_suffix])
    recipient_qset = User.objects.none() #put recipients in a QuerySet
    
    if msg.to == "all" :
        recipient_qset = course.get_all_members()
    elif msg.to == "students" :
        recipient_qset = course.get_all_students()
    elif msg.to == "staff" :
        recipient_qset = course.get_all_course_admins()
    elif msg.to == "myself":
        recipient_qset = User.objects.filter(id=msg.sender.id)

    chunk=int(math.ceil(float(recipient_qset.count())/float(num_workers)))
    recipient_qset=recipient_qset[worker_id*chunk:worker_id*chunk+chunk]

    connection = get_connection() #get mail connection from settings
    connection.open()
    num_sent=0

    for user in recipient_qset.only('first_name','last_name','email'):
        html_footer = render_to_string('email/email_footer.html',
                                       {'course_title':course_title,
                                       'url':course_url,
                                       'first_name':user.first_name,
                                       'last_name':user.last_name,
                                       'email':user.email,
                                       })
        
        plain_footer = render_to_string('email/email_footer.txt',
                                        {'course_title':course_title,
                                        'url':course_url,
                                        'first_name':user.first_name,
                                        'last_name':user.last_name,
                                        'email':user.email,
                                        })
        
        email_msg = EmailMultiAlternatives(msg.subject, plaintext+plain_footer, from_addr, [user.email], connection=connection)
        email_msg.attach_alternative(msg.html_message+html_footer,'text/html')
        connection.open() ##safe to call many times b/c will just return if connection already exists
        
        connection.send_messages([email_msg])
        num_sent +=1

    connection.close()
    return num_sent

@task()
def email_with_celery(subject,html_msg,sender,recipient_email_list,course_title='',course_url=''):
    """
    Takes a subject and an html formatted email and sends it from sender to all addresses
    in the to_list, with each recipient being the only "to".  Emails are sent multipart, in both
    plain text and html.  Send using celery task
    """

    p = Popen(['lynx','-stdin','-dump'], stdin=PIPE, stdout=PIPE)
    (plaintext, err_from_stderr) = p.communicate(input=html_msg) #use lynx to get plaintext
    
    connection = get_connection() #get connection from settings
    connection.open()
    num_sent=0
    for to_email in recipient_email_list:
        users = User.objects.filter(email=to_email)
        for user in users:
            html_footer = render_to_string('email/email_footer.html',
                                        {'course_title':course_title,
                                        'url':course_url,
                                        'first_name':user.first_name,
                                        'last_name':user.last_name,
                                        'email':user.email,
                                        })
    
            plain_footer = render_to_string('email/email_footer.txt',
                                        {'course_title':course_title,
                                        'url':course_url,
                                        'first_name':user.first_name,
                                        'last_name':user.last_name,
                                        'email':user.email,
                                        })
        
            msg = EmailMultiAlternatives(subject, plaintext+plain_footer, sender, [user.email], connection=connection)
            msg.attach_alternative(html_msg+html_footer,'text/html')
            connection.send_messages([msg])
            num_sent += 1
    connection.close()
    return num_sent


