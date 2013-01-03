from django.core.mail import EmailMultiAlternatives, get_connection
from subprocess import Popen, PIPE, STDOUT
from celery import task
from time import sleep
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from c2g.models import Course, CourseEmail, ListEmail
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from collections import deque
from smtplib import SMTPException, SMTPServerDisconnected, SMTPDataError, SMTPConnectError
from celery.task import current
from django.contrib.sites.models import Site

import random
import math
import time
import re
import logging
logger = logging.getLogger(__name__)

EMAILS_PER_WORKER=getattr(settings, 'EMAILS_PER_WORKER', 10)





@task()
def delegate_list_emails(hash_for_msg):
    '''
    Delegates the celery tasks to send an email given a msg_hash
    '''
    email_from_db=ListEmail.objects.get(hash=hash_for_msg)
    recipient_qset = email_from_db.to_list.members.all()
    total_num_emails = recipient_qset.count()
    num_workers=int(math.ceil(float(total_num_emails)/float(EMAILS_PER_WORKER)))
    recipient_list = map(lambda r: (r.name, r.addr, r.optout, r.optout_code), list(recipient_qset))
            
    chunk=int(math.ceil(float(total_num_emails)/float(num_workers)))
            
    for i in range(num_workers):
        to_list=recipient_list[i*chunk:i*chunk+chunk]
        email_list.delay(hash_for_msg, to_list, False)
            
    return num_workers




@task(default_retry_delay=15, max_retries=5)
def email_list(msg_hash, addr_list, throttle=False):
    '''Sends ListEmail identifed by msg_hash to all recipients in addr_list
       Sends multipart
    '''
    
    email_from_db=ListEmail.objects.get(hash=msg_hash)
    if (not email_from_db.from_name) or (not email_from_db.from_addr):
        return 0
    from_addr = email_from_db.from_name + "<%s>" % email_from_db.from_addr

    site = Site.objects.get(id=1) # Counts on there being one site in the db.

    try:
        connection = get_connection() #get mail connection from settings
        connection.open()
        num_sent=0
        num_error=0
        
        rg = random.SystemRandom(random.randint(0,100000))

        while addr_list:
            (name, email, optout, code) = addr_list[-1]
            if optout:
                logger.info('Email with hash ' + msg_hash + ' NOT sent b/c OPTOUT ' + email)

            else:
                html_msg = render_to_string('email/email_marketing.html',
                            {'message':email_from_db.html_message,
                             'optout_code':code,
                             'domain':site.domain
                            })
                p = Popen(['lynx','-stdin','-display_charset=UTF-8','-assume_charset=UTF-8','-dump'], stdin=PIPE, stdout=PIPE)
                (plaintext, err_from_stderr) = p.communicate(input=html_msg.encode('utf-8')) #use lynx to get plaintext
                if err_from_stderr:
                    logger.info(err_from_stderr)
        
                to_string = name + " <%s>" % email
                email_msg = EmailMultiAlternatives(email_from_db.subject, plaintext, from_addr, [to_string], connection=connection)
                email_msg.attach_alternative(html_msg,'text/html')
            
                if throttle or current.request.retries > 0: #throttle if we tried a few times and got the rate limiter
                    time.sleep(0.2)
                
                try: #nested try except blocks.
                    #CHAOS!
                    #if rg.randint(0,25) == 1:
                    #    logger.info('RAISE 400!')
                    #    raise SMTPDataError(400,'Randomly generated exception that should be retried.')
                    #if rg.randint(0,25) == 1:
                    #    logger.info('RAISE 500!')
                    #    raise SMTPDataError(500,'Randomly generated exception that should NOT be retried.')
                    connection.send_messages([email_msg])
                    logger.info('Email with hash ' + msg_hash + ' sent to ' + email)
                    num_sent +=1

                except SMTPDataError as exc:
                    #code map so far
                    #554 : Message rejected: Address blacklisted
                    #554 : Transaction failed: Missing final @domain
                    #454 : Throttling failure: Maximum sending rate exceeded
                    #According to SMTP spec, we'll retry error codes in the 4xx range.  5xx range indicates hard failure
                    if exc.smtp_code >= 400 and exc.smtp_code < 500:
                        raise exc # this will cause the outer handler to catch the exception and retry the entire task
                    else:
                        #this will fall through and not retry the message, since it will be popped
                        logger.warn('Email with hash ' + msg_hash + ' not delivered to ' + email + ' due to error: ' + exc.smtp_error)
                        num_error += 1
                        connection.open() #reopen connection, in case error closed it


            addr_list.pop()

        connection.close()
        return "Sent %d, Fail %d" % (num_sent, num_error)

    except (SMTPDataError, SMTPConnectError, SMTPServerDisconnected) as exc:
        #error caught here cause the email to be retried.  The entire task is actually retried without popping the list
        raise email_list.retry(arg=[msg_hash, addr_list, current.request.retries>0], exc=exc, countdown=(2 ** current.request.retries)*15)


@task()
def delegate_emails(hash_for_msg, total_num_emails, course_title, course_handle, course_url, query ):
    '''Delegates emails by spinning up appropriate number of sender workers
       Tries to minimize DB accesses performed by each worker.
       Especially passing query forming a queryset, which is ok practice according
       to https://docs.djangoproject.com/en/dev/ref/models/querysets/#pickling-querysets
    '''
    num_workers=int(math.ceil(float(total_num_emails)/float(EMAILS_PER_WORKER)))
    recipient_qset = User.objects.all() #put recipients in a QuerySet
    recipient_qset.query = query #again, this is supported practice for reconstructing a queryset from a pickle,
    recipient_qset = recipient_qset.filter(userprofile__email_me=True) #respect student email optout
    recipient_qset.only('email','first_name','last_name')
    recipient_list = map(lambda r: (r.first_name, r.last_name, r.email), list(recipient_qset))
    
    chunk=int(math.ceil(float(total_num_emails)/float(num_workers)))

    for i in range(num_workers):
        to_list=recipient_list[i*chunk:i*chunk+chunk]
        course_email_with_celery.delay(hash_for_msg, to_list, False, course_title, course_handle, course_url)
    return num_workers



@task(default_retry_delay=15, max_retries=5)
def course_email_with_celery(hash_for_msg, to_list,  throttle=False, course_title='', course_handle='', course_url=''):
    """
        Takes a subject and an html formatted email and sends it from sender to all addresses
        in the to_list, with each recipient being the only "to".  Emails are sent multipart, in both
        plain text and html.  Send using celery task.
        
        For work division, this task can be called with num_workers and worker_id, where num_workers is the
        total number of workers and worker_id is the id of this worker, 
        out of a set with ids 0 to num_workers-1, in homage to the fact that python lists are zero based.
    """
    msg = CourseEmail.objects.get(hash=hash_for_msg)
    
    p = Popen(['lynx','-stdin','-display_charset=UTF-8','-assume_charset=UTF-8','-dump'], stdin=PIPE, stdout=PIPE)
    (plaintext, err_from_stderr) = p.communicate(input=msg.html_message.encode('utf-8')) #use lynx to get plaintext
    staff_email = 'noreply@class2go.stanford.edu'
    if course_handle:
        staff_email = re.sub(r'\--', r'-',course_handle) + '-staff@class2go.stanford.edu'
    course_title_no_quotes = re.sub(r'"', '', course_title) # strip out all quotes
    from_addr = '"%s" Course Staff <%s>' % (course_title_no_quotes, staff_email) #make certain that we quote the name part of the email address

    if err_from_stderr:
        logger.info(err_from_stderr)

    try:

        connection = get_connection() #get mail connection from settings
        connection.open()
        num_sent=0
        num_error=0

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
            email_msg = EmailMultiAlternatives(msg.subject, plaintext+plain_footer.encode('utf-8'), from_addr, [email], connection=connection)
            email_msg.attach_alternative(msg.html_message+html_footer.encode('utf-8'),'text/html')
            
            if throttle or current.request.retries > 0: #throttle if we tried a few times and got the rate limiter
                time.sleep(0.2)

            
            try: #nested try except blocks.
                #CHAOS!
                #if rg.randint(0,25) == 1:
                #    logger.info('RAISE 400!')
                #    raise SMTPDataError(400,'Randomly generated exception that should be retried.')
                #if rg.randint(0,25) == 1:
                #    logger.info('RAISE 500!')
                #    raise SMTPDataError(500,'Randomly generated exception that should NOT be retried.')

                connection.send_messages([email_msg])
                logger.info('Email with hash ' + hash_for_msg + ' sent to ' + email)
                num_sent +=1

            except SMTPDataError as exc:
                #code map so far
                #554 : Message rejected: Address blacklisted
                #554 : Transaction failed: Missing final @domain
                #454 : Throttling failure: Maximum sending rate exceeded
                #According to SMTP spec, we'll retry error codes in the 4xx range.  5xx range indicates hard failure
                if exc.smtp_code >= 400 and exc.smtp_code < 500:
                    raise exc # this will cause the outer handler to catch the exception and retry the entire task
                else:
                    #this will fall through and not retry the message, since it will be popped
                    logger.warn('Email with hash ' + hash_for_msg + ' not delivered to ' + email + ' due to error: ' + exc.smtp_error)
                    num_error += 1
                    connection.open() #reopen connection, in case.

            
            to_list.pop()
        
        connection.close()
        return "Sent %d, Fail %d" % (num_sent, num_error)

    except (SMTPDataError, SMTPConnectError, SMTPServerDisconnected) as exc:
        raise course_email_with_celery.retry(arg=[hash_for_msg, to_list, current.request.retries>0, course_title, course_handle,
                                                  course_url], exc=exc, countdown=(2 ** current.request.retries)*15)


@task()
def email_with_celery(subject,html_msg,sender,recipient_email_list,course_title='',course_url=''):
    """
    Takes a subject and an html formatted email and sends it from sender to all addresses
    in the to_list, with each recipient being the only "to".  Emails are sent multipart, in both
    plain text and html.  Send using celery task
    """

    p = Popen(['lynx','-stdin','-display_charset=UTF-8','-assume_charset=UTF-8','-dump'], stdin=PIPE, stdout=PIPE)
    (plaintext, err_from_stderr) = p.communicate(input=html_msg.encode('utf-8')) #use lynx to get plaintext
    
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
        
            msg = EmailMultiAlternatives(msg.subject, plaintext+plain_footer.encode('utf-8'), from_addr, [email], connection=connection)
            msg.attach_alternative(html_msg+html_footer.encode('utf-8'),'text/html')
            connection.send_messages([msg])
            num_sent += 1
    connection.close()
    return num_sent


