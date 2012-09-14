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
from collections import deque
from smtplib import SMTPException
from celery.task import current

import random
import math
import time
import logging
logger = logging.getLogger(__name__)

EMAILS_PER_WORKER=getattr(settings, 'EMAILS_PER_WORKER', 10)

@task()
def delegate_emails(hash_for_msg, total_num_emails, course_title, course_url, query ):
    '''Delegates emails by spinning up appropriate number of sender workers
       Tries to minimize DB accesses performed by each worker.
       Especially passing query forming a queryset, which is ok practice according
       to https://docs.djangoproject.com/en/dev/ref/models/querysets/#pickling-querysets
    '''
    num_workers=int(math.ceil(float(total_num_emails)/float(EMAILS_PER_WORKER)))
    recipient_qset = User.objects.all() #put recipients in a QuerySet
    recipient_qset.query = query #again, this is supported practice for reconstructing a queryset from a pickle,
    recipient_qset.only('email','first_name','last_name')
    recipient_list = map(lambda r: (r.first_name, r.last_name, r.email), list(recipient_qset))
    
    chunk=int(math.ceil(float(total_num_emails)/float(num_workers)))

    for i in range(num_workers):
        to_list=recipient_list[i*chunk:i*chunk+chunk]
        course_email_with_celery.delay(hash_for_msg, to_list, False, course_title, course_url)
    return num_workers



@task(default_retry_delay=15, max_retries=5)
def course_email_with_celery(hash_for_msg, to_list,  throttle=False, course_title='', course_url=''):
    """
        Takes a subject and an html formatted email and sends it from sender to all addresses
        in the to_list, with each recipient being the only "to".  Emails are sent multipart, in both
        plain text and html.  Send using celery task.
        
        For work division, this task can be called with num_workers and worker_id, where num_workers is the
        total number of workers and worker_id is the id of this worker, 
        out of a set with ids 0 to num_workers-1, in homage to the fact that python lists are zero based.
    """
    msg = CourseEmail.objects.get(hash=hash_for_msg)
    
    p = Popen(['lynx','-stdin','-dump'], stdin=PIPE, stdout=PIPE)
    (plaintext, err_from_stderr) = p.communicate(input=msg.html_message) #use lynx to get plaintext
    from_addr = course_title + ' Staff <class2go-noreply@cs.stanford.edu>'

    if err_from_stderr:
        logger.info(err_from_stderr)

    try:

        connection = get_connection() #get mail connection from settings
        connection.open()
        num_sent=0

        rg = random.SystemRandom(random.randint(0,100000))

        while to_list:
            (first_name, last_name, email) = to_list[-1]
            html_footer = render_to_string('email/email_footer.html',
                                           {'course_title':course_title,
                                           'url':course_url,
                                           'first_name':first_name,
                                           'last_name':last_name,
                                           'email':email,
                                           })
            
            plain_footer = render_to_string('email/email_footer.txt',
                                            {'course_title':course_title,
                                            'url':course_url,
                                            'first_name':first_name,
                                            'last_name':last_name,
                                            'email':email,
                                            })
            
            email_msg = EmailMultiAlternatives(msg.subject, plaintext+plain_footer, from_addr, [email], connection=connection)
            email_msg.attach_alternative(msg.html_message+html_footer,'text/html')
            
            if throttle or current.request.retries > 0: #throttle if we tried a few times and got the rate limiter
                time.sleep(0.2)

            
            #CHAOS!
            #if rg.randint(0,50) == 1:
            #   raise SMTPException(1,'Randomly generated exception to test email robustness')

            connection.send_messages([email_msg])
            logger.info('Email with hash ' + hash_for_msg + ' sent to ' + email)
            
            num_sent +=1
            to_list.pop()
        
        connection.close()
        return num_sent

    except SMTPException as exc:
        raise course_email_with_celery.retry(arg=[hash_for_msg, to_list, current.request.retries>0, course_title,
                                                  course_url], exc=exc, countdown=(2 ** current.request.retries)*15)


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


