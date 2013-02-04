# Create your views here.
import sys
import traceback
import json
import operator
import logging
import settings
import datetime
import csv
import HTMLParser
import json
from django.db.models import Sum, Max, F
import copy
import urllib2, urlparse
from xml.dom.minidom import parseString


FILE_DIR = getattr(settings, 'FILE_UPLOAD_TEMP_DIR', '/tmp')
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
AWS_SECURE_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_SECURE_STORAGE_BUCKET_NAME', '')

logger = logging.getLogger(__name__)

from c2g.models import ContentGroup, Exercise, Video, VideoToExercise, ProblemSet, ProblemSetToExercise, Exam, ExamRecord, ExamScore, ExamScoreField, ExamRecordScore, ExamRecordScoreField, ExamRecordFieldLog, ExamRecordScoreFieldChoice, ContentSection, parse_video_exam_metadata, StudentExamStart
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from django.core.validators import validate_slug, ValidationError
from django.core.exceptions import MultipleObjectsReturned
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper, create_contentgroup_entries_from_post
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.utils import encoding
from courses.exams.autograder import AutoGrader, AutoGraderException, AutoGraderGradingException
from courses.course_materials import get_course_materials
from django.views.decorators.csrf import csrf_protect
from storages.backends.s3boto import S3BotoStorage


@auth_view_wrapper
def listAll(request, course_prefix, course_suffix, show_types=["exam",]):
    
    course = request.common_page_data['course']
    if course.mode == "draft": #draft mode, lists grades
        exams = list(Exam.objects.filter(course=course, is_deleted=0, exam_type__in=show_types))

        #if course.mode=="live":
            #exams = filter(lambda item: item.is_live(), exams)
        
        scores = []

        for e in exams:
            if ExamScore.objects.filter(course=course, exam=e, student=request.user).exists():
                scores.append(ExamScore.objects.filter(course=course, exam=e, student=request.user)[0].score)
            else:
                scores.append(None)

        return render_to_response('exams/list.html',
                                  {'common_page_data':request.common_page_data,
                                   'course':course,
                                  'exams_and_scores':zip(exams,scores)},
                                  RequestContext(request))
    else: #ready mode, uses section structures
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=False, get_exam_content=True, exam_types=show_types)
        
        form = None
        
        if show_types:
            ex_type = show_types[0]
        else:
            ex_type = "exam"
            
        
        
        return render_to_response('exams/ready/list.html', {'common_page_data': request.common_page_data, 'section_structures':section_structures, 'reverse_show':ex_type+'_show', 'form':form, }, context_instance=RequestContext(request))


@auth_view_wrapper
def confirm(request, course_prefix, course_suffix, exam_slug):
    
    course = request.common_page_data['course']
        
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    slug_for_leftnav = exam_slug

    ready_section = exam.section
    if ready_section and ready_section.mode == "draft":
        ready_section = ready_section.image

    minutesallowed = exam.minutesallowed if exam.minutesallowed else 999

    allowed_timedelta = datetime.timedelta(minutes=minutesallowed)

    endtime = datetime.datetime.now() + allowed_timedelta

    return render_to_response('exams/confirm.html',
                              {'common_page_data':request.common_page_data, 'course': course, 'exam':exam, 'ready_section':ready_section,
                              'endtime': endtime, 'slug_for_leftnav':slug_for_leftnav, 'minutesallowed':minutesallowed,
                              }, RequestContext(request))


# Create your views here.
@auth_view_wrapper
def show_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    too_many_attempts = exam.max_attempts_exceeded(request.user)

    too_recent = False
    last_record = last_completed_record(exam, request.user, include_contentgroup=True)

    if last_record and (datetime.datetime.now() - last_record.last_updated) < datetime.timedelta(minutes=exam.minutes_btw_attempts):
        too_recent = True

    if (not too_many_attempts) and (not too_recent) and exam.timed \
        and request.GET.get("confirm", "") != "True" and not StudentExamStart.objects.filter(student=request.user, exam=exam).exists():
        return HttpResponseRedirect(reverse('confirm_exam_start', args=(course.prefix, course.suffix, exam.slug)))


    ready_section = exam.section
    if ready_section and ready_section.mode == "draft":
        ready_section = ready_section.image

    #Get the slug of the parent exam of all variations, which we need to highlight in the left navbar
    try:
        cginfo = ContentGroup.groupinfo_by_id('exam', exam.id)
        parent_tag = cginfo.get('__parent_tag', '')
        parent = cginfo.get('__parent', None)
        if parent_tag != 'exam':
            slug_for_leftnav = exam.slug
        elif not parent:
            slug_for_leftnav = exam.slug
        else:
            slug_for_leftnav = parent.slug
    except ContentGroup.DoesNotExist:
        slug_for_leftnav = exam.slug

    incomplete_record = get_or_update_incomplete_examrecord(course, exam, request.user)

    #Code for timed exam
    timeopened = datetime.datetime.now()

    editable = not exam.past_due()  #editable controls whether the inputs are enabled or disabled
    allow_submit = not exam.past_due() #allow submit controls whether diabled inputs can be reenabled and whether to show the submit button

    if exam.timed:
        startobj, created = StudentExamStart.objects.get_or_create(student=request.user, exam=exam)
        endtime = startobj.time_created + datetime.timedelta(minutes=exam.minutesallowed)
        
        if timeopened > endtime :
            editable = False
            allow_submit = False
                
    else:
        endtime = None


    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data,
                              'json_pre_pop':incomplete_record.json_data, 'too_recent':too_recent,
                              'last_record':last_record, 'ready_section':ready_section, 'slug_for_leftnav':slug_for_leftnav,
                              'scores':"{}",'editable':editable,'single_question':exam.display_single,'videotest':False,
                              'allow_submit':allow_submit, 'too_many_attempts':too_many_attempts,
                              'endtime':endtime, 'timeopened':timeopened,
                              'exam':exam,}, RequestContext(request))

def last_completed_record(exam, student, include_contentgroup=False):
    """Helper function to get the last completed record of this exam.
       If include_contentgroup is True, will include records from
       all of the other exams in the contentgroup.
    """
    try:
        if include_contentgroup:
            cginfo = ContentGroup.groupinfo_by_id('exam',exam.id)
            exam_list = cginfo.get('exam',[exam]) #default to a singleton list consisting of just this exam
            record = ExamRecord.objects.filter(exam__in=exam_list, complete=True, student=student).latest('last_updated')
        else:
            record = ExamRecord.objects.filter(exam=exam, complete=True, student=student).latest('last_updated')
        return record

    except ExamRecord.DoesNotExist:
        return None

@require_POST
@auth_view_wrapper
def show_populated_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    parser = HTMLParser.HTMLParser()
    json_pre_pop = parser.unescape(request.POST['json-pre-pop'])
    json_pre_pop_correx = parser.unescape(request.POST['json-pre-pop-correx'])
    scores = request.POST.get('scores',"{}")
    editable = request.POST.get('latest', False)
 
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    too_many_attempts = exam.max_attempts_exceeded(request.user)

    ready_section = exam.section
    if ready_section and ready_section.mode == "draft":
        ready_section = ready_section.image

    #Get the slug of the parent exam of all variations, which we need to highlight in the left navbar
    try:
        cginfo = ContentGroup.groupinfo_by_id('exam', exam.id)
        parent_tag = cginfo.get('__parent_tag', '')
        parent = cginfo.get('__parent', None)
        if parent_tag != 'exam':
            slug_for_leftnav = exam.slug
        elif not parent:
            slug_for_leftnav = exam.slug
        else:
            slug_for_leftnav = parent.slug
    except ContentGroup.DoesNotExist:
        slug_for_leftnav = exam.slug


    #Code for timed exams
    allow_submit = not exam.past_due() #allow submit controls whether diabled inputs can be reenabled and whether to show the submit button
        
    timeopened = datetime.datetime.now()
    
    if exam.timed:
        startobj, created=StudentExamStart.objects.get_or_create(student=request.user, exam=exam)
        endtime = startobj.time_created + datetime.timedelta(minutes=exam.minutesallowed)
        
        if timeopened > endtime :
            editable = False
            allow_submit = False
    else:
        endtime = None

    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop,
                                                       'slug_for_leftnav':slug_for_leftnav, 'ready_section':ready_section,
                                                       'json_pre_pop_correx':json_pre_pop_correx, 'scores':scores, 'editable':editable, 'endtime':endtime,
                                                       'allow_submit':allow_submit, 'timeopened':timeopened, 'too_many_attempts':too_many_attempts},
                              RequestContext(request))

@auth_view_wrapper
def show_graded_exam(request, course_prefix, course_suffix, exam_slug, type="exam"):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    try:
        record = ExamRecord.objects.filter(course=course, exam=exam, student=request.user, complete=True, time_created__lt=exam.grace_period).latest('time_created')
        #call show_graded_record to for code reuse
        return show_graded_record(request, course_prefix, course_suffix, exam_slug, record.id, type=type)
        
    except ExamRecord.DoesNotExist:
        raise Http404


@auth_view_wrapper
def show_graded_record(request, course_prefix, course_suffix, exam_slug, record_id, type="exam"):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404
    
    try:
        #the addition of the user filter performs access control
        record = ExamRecord.objects.get(id=record_id, course=course, exam=exam, student=request.user, complete=True)
        json_pre_pop = record.json_data
        if record.json_score_data:
            correx_obj = json.loads(record.json_score_data)
        else:
            correx_obj = {}

        correx_obj['__metadata__'] = exam.xml_metadata if exam.xml_metadata else "<empty></empty>"
        json_pre_pop_correx = json.dumps(correx_obj)
        score = record.score

    except ExamRecord.DoesNotExist:
        raise Http404


    try:
        score_obj = ExamRecordScore.objects.get(record=record)
        raw_score = score_obj.raw_score
        score_fields = {}
        for s in list(ExamRecordScoreField.objects.filter(parent=score_obj)):
            score_fields[s.field_name] = s.subscore
        scores_json = json.dumps(score_fields)

    except ExamRecordScore.DoesNotExist, ExamRecordScore.MultipleObjectsReturned:
        raw_score = None
        scores_json = "{}"

    ready_section = exam.section
    if ready_section and ready_section.mode == "draft":
        ready_section = ready_section.image

    #Get the slug of the parent exam of all variations, which we need to highlight in the left navbar
    try:
        cginfo = ContentGroup.groupinfo_by_id('exam', exam.id)
        parent_tag = cginfo.get('__parent_tag', '')
        parent = cginfo.get('__parent', None)
        if parent_tag != 'exam':
            slug_for_leftnav = exam.slug
        elif not parent:
            slug_for_leftnav = exam.slug
        else:
            slug_for_leftnav = parent.slug
    except ContentGroup.DoesNotExist:
        slug_for_leftnav = exam.slug

    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop, 'scores':scores_json, 'score':score, 'json_pre_pop_correx':json_pre_pop_correx, 'editable':False, 'raw_score':raw_score, 'allow_submit':False, 'ready_section':ready_section, 'slug_for_leftnav':slug_for_leftnav}, RequestContext(request))




@auth_view_wrapper
def view_my_submissions(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    subs = list(ExamRecord.objects.filter(course=course, exam=exam, student=request.user, complete=True, time_created__lt=exam.grace_period).order_by('-time_created'))

    my_subs = map(lambda s: my_subs_helper(s), subs)

    try:
        score_obj = ExamScore.objects.get(course=course, exam=exam, student=request.user)
        score = score_obj.score
        score_fields = {}
        for s in list(ExamScoreField.objects.filter(parent=score_obj)):
            score_fields[s.field_name] = s.subscore

    except ExamScore.DoesNotExist, ExamScore.MultipleObjectsReturned:
        score = None
        score_fields = {}

    return render_to_response('exams/view_my_submissions.html', {'common_page_data':request.common_page_data, 'exam':exam, 'my_subs':my_subs,
                              'score_fields':json.dumps(score_fields), 'score':score}, RequestContext(request) )


def my_subs_helper(s):
    """Helper function to handle badly formed JSON stored in the database"""
    try:
        return {'time_created':s.time_created, 'json_obj':sorted(json.loads(s.json_data).iteritems(), key=operator.itemgetter(0)), 'plain_json_obj':json.dumps(json.loads(s.json_data)),'id':s.id, 'json_score_data':json.dumps(s.json_score_data)}
    except ValueError:
        return {'time_created':s.time_created, 'json_obj':"__ERROR__", 'plain_json_obj':"__ERROR__", 'id':s.id}

@auth_is_course_admin_view_wrapper
def view_submissions_to_grade(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    if exam.mode=="draft":
        exam = exam.image

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
    outfile.seek(0)
    s3file.write(outfile.read())
    s3file.close()
    outfile.close()
    return HttpResponseRedirect(secure_file_storage.url_monkeypatched("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname), response_headers={'response-content-disposition': 'attachment'}))

def parse_val(v):
    """Helper function to parse AJAX submissions"""
    if isinstance(v,list):
        sorted_list = sorted(map(lambda li: li['value'], v))
        return reduce(lambda x,y: x+y+",", sorted_list, "")
    else:
        try:
           return v.get('value', "")
        except TypeError, AttributeError:
            return str(v)


@require_POST
@auth_view_wrapper
def collect_data(request, course_prefix, course_suffix, exam_slug):
    
    course = request.common_page_data['course']
    user = request.user
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    postdata = request.POST['json_data'] #will return an error code to the user if either of these fail (throws 500)
    json_obj=json.loads(postdata)

    if exam.mode == "ready" and exam.past_all_deadlines():
        return HttpResponseBadRequest("Sorry!  This submission is past the last deadline of %s" % \
                                      datetime.datetime.strftime(exam.partial_credit_deadline, "%m/%d/%Y %H:%M PST"));

    if exam.timed:
        try:
            started = StudentExamStart.objects.get(exam=exam, student=user)
            endtime = started.time_created + datetime.timedelta(minutes = (exam.minutesallowed+1))
            if datetime.datetime.now() > endtime:
                return HttpResponseBadRequest("Sorry!  This submission is past your submission window, which ended at %s" % \
                                              datetime.datetime.strftime(endtime, "%m/%d/%Y %H:%M PST"));
        except StudentExamStart.DoesNotExist:
            pass #somehow we didn't record a start time for the student.  So we just let them submit.

    attempt_number = exam.num_of_student_records(user)+1

    onpage = request.POST.get('onpage','')
    
    record = ExamRecord(course=course, exam=exam, student=user, json_data=postdata, onpage=onpage, attempt_number=attempt_number, late=exam.past_due())
    record.save()

    autograder = None

    if exam.exam_type == "survey":
        autograder = AutoGrader("<null></null>", default_return=True) #create a null autograder that always returns the "True" object
    elif exam.autograde:
        try:
            autograder = AutoGrader(exam.xml_metadata)
        except Exception as e: #Pass back all the exceptions so user can see
            return HttpResponseBadRequest(unicode(e))

    if autograder:

        record_score = ExamRecordScore(record = record)
        record_score.save()

        feedback = {}
        total_score = 0
        for prob,v in json_obj.iteritems():  #prob is the "input" id, v is the associated value,
                                             #which can be an object (input box) or a list of objects (multiple-choice)
            try:
                if isinstance(v,list): #multiple choice case
                    submission = map(lambda li: li['value'], v)
                    feedback[prob] = autograder.grade(prob, submission)
                    field_obj = ExamRecordScoreField(parent=record_score,
                                                     field_name = prob,
                                                     human_name=v[0].get('questionreport', "") if len(v)>0 else "",
                                                     subscore = feedback[prob]['score'],
                                                     value = map(lambda li:li.encode('utf-8'),submission),
                                                     correct = feedback[prob]['correct'],
                                                     comments="",
                                                     associated_text = v[0].get('associatedText', "") if len(v)>0 else "",
                                                     )
                    field_obj.save()
                    for li in v:
                        if 'correct_choices' not in feedback[prob]:
                            is_correct = None
                        else:
                            is_correct = li['value'] in feedback[prob]['correct_choices']                        
                        fc = ExamRecordScoreFieldChoice(parent=field_obj,
                                                        choice_value=li['value'],
                                                        correct=is_correct,
                                                        human_name=li.get('report',""),
                                                        associated_text=li.get('associatedText',""))
                        fc.save()
                
                else: #single answer
                    submission = v['value']
                    feedback[prob] = autograder.grade(prob, submission)
                    field_obj = ExamRecordScoreField(parent=record_score,
                                 field_name = prob,
                                 human_name=v.get('report', ""),
                                 subscore = feedback[prob]['score'],
                                 value = submission,
                                 correct = feedback[prob]['correct'],
                                 comments="",
                                 associated_text = v.get('associatedText', ""))
                    field_obj.save()
            except AutoGraderGradingException as e:
                feedback[prob]={'correct':False, 'score':0}
                field_obj = ExamRecordScoreField(parent=record_score,
                                 field_name = prob,
                                 human_name=v.get('report', ""),
                                 subscore = 0,
                                 correct = feedback[prob]['correct'],
                                 comments = unicode(e),
                                 associated_text = v.get('associatedText', ""))
                field_obj.save()
            #This is when using code indents to denote blocks is a bit hairy
            #supposed to be at the same level as try...except.  Run once per prob,v
            total_score += feedback[prob]['score']

        #Set raw score for ExamRecordScore
        record_score.raw_score = total_score
        record_score.save()

        #Set penalty inclusive score for ExamRecord
        record.json_score_data = json.dumps(feedback)
        
        #apply penalties
        record.score = compute_penalties(total_score, attempt_number, exam.resubmission_penalty, record.late, exam.late_penalty)
        record.save()
        
        #Set ExamScore.score to max of ExamRecord.score for that student, exam. 
        exam_score, created = ExamScore.objects.get_or_create(course=course, exam=exam, student=user)
        exam_score.setScore()

        return HttpResponse(reverse(exam.record_view, args=[course.prefix, course.suffix, exam.slug, record.id]))

    else:
        return HttpResponse("Submission has been saved.")


def compute_penalties(raw_score, attempt_number, resubmission_penalty, is_late, late_penalty):
    """Helper function to factor out resubmission and late penalty calculations, 
       so I can write a few unit tests for it
    """
    resubmission_discount = pow(max(0.0, (100.0 - resubmission_penalty)/100.0), (attempt_number - 1))
    score = raw_score * resubmission_discount
    late_discount = max(0.0, 100.0 - late_penalty)/100.0
    if is_late:
        score *= late_discount
    return max(score, 0.0)

@require_POST
@auth_is_course_admin_view_wrapper
def edit_exam_ajax_wrapper(request, course_prefix, course_suffix, exam_slug):
    return save_exam_ajax(request, course_prefix, course_suffix, create_or_edit="edit", old_slug=exam_slug)


@require_POST
@auth_is_course_admin_view_wrapper
def save_exam_ajax(request, course_prefix, course_suffix, create_or_edit="create", old_slug=""):
    course = request.common_page_data['course']
    if course.mode == "ready":
        course = course.image
    
    slug = request.POST.get('slug','')
    title = request.POST.get('title', '')
    description = request.POST.get('description', '')
    metaXMLContent = request.POST.get('metaXMLContent', '')
    htmlContent = request.POST.get('htmlContent', '')
    xmlImported = request.POST.get('xmlImported','')
    due_date = request.POST.get('due_date', '')
    grace_period = request.POST.get('grace_period', '')
    partial_credit_deadline =  request.POST.get('partial_credit_deadline', '')
    late_penalty = request.POST.get('late_penalty', '')
    num_subs_permitted = request.POST.get('num_subs_permitted','')
    resubmission_penalty = request.POST.get('resubmission_penalty','')
    assessment_type = request.POST.get('assessment_type','')
    section=request.POST.get('section','')
    invideo_val=request.POST.get('invideo','')
    
    if invideo_val and invideo_val == "true":
        invideo = True
    else:
        invideo = False

    #########Validation, lots of validation#######
    if not slug:
        return HttpResponseBadRequest("No URL identifier value provided")
    try:
        validate_slug(slug)
    except ValidationError as ve:
        return HttpResponseBadRequest(unicode(ve))

    if not title:
        return HttpResponseBadRequest("No Title value provided")
    if not metaXMLContent:
        return HttpResponseBadRequest("No metadataXML provided")
    try:
        grader = AutoGrader(metaXMLContent)
    except Exception as e: #Since this is just a validator, pass back all the exceptions
        return HttpResponseBadRequest(unicode(e))

    total_score = grader.points_possible

    if not htmlContent:
        return HttpResponseBadRequest("No Exam HTML provided")
    if not due_date:
        return HttpResponseBadRequest("No due date provided")
    if not grace_period:
        return HttpResponseBadRequest("No grace period provided")
    if not partial_credit_deadline:
        return HttpResponseBadRequest("No hard deadline provided")
    if not section:
        return HttpResponseBadRequest("Bad section provided!")

    try:
        contentsection = ContentSection.objects.get(id=section, course=course, is_deleted=False)
    except ContentSection.DoesNotExist:
        return HttpResponseBadRequest("Bad section provided!")

    dd = datetime.datetime.strptime(due_date, "%m/%d/%Y %H:%M")
    gp = datetime.datetime.strptime(grace_period, "%m/%d/%Y %H:%M")
    pcd = datetime.datetime.strptime(partial_credit_deadline, "%m/%d/%Y %H:%M")

    if assessment_type == "summative":
        autograde = True
        display_single = False
        grade_single = False
        exam_type = "problemset"
    elif assessment_type == "formative":
        autograde = True
        display_single = True
        grade_single = False #We will eventually want this to be True
        exam_type = "problemset"
    elif assessment_type == "interactive":
        autograde = True
        display_single = True
        grade_single = False
        exam_type = "interactive_exercise"
    elif assessment_type == "exam-autograde":
        autograde = True
        display_single = False
        grade_single = False
        exam_type = "exam"
    elif assessment_type == "exam-csv":
        autograde = False
        display_single = False
        grade_single = False
        exam_type = "exam"
    elif assessment_type == "survey":
        autograde = False
        display_single = False
        grade_single = False
        exam_type = "survey"
    else:
        return HttpResponseBadRequest("A bad assessment type (" + assessment_type  + ") was provided")

    if not late_penalty:
        lp = 0
    else:
        try:
            lp = int(late_penalty)
        except ValueError:
            return HttpResponseBadRequest("A non-numeric late penalty (" + late_penalty  + ") was provided")

    if not num_subs_permitted:
        sp = 999
    else:
        try:
            sp = int(num_subs_permitted)
        except ValueError:
            return HttpResponseBadRequest("A non-numeric number of submissions permitted (" + sp  + ") was provided")

    if not resubmission_penalty:
        rp = 0
    else:
        try:
            rp = int(resubmission_penalty)
        except ValueError:
            return HttpResponseBadRequest("A non-numeric resubmission penalty (" + resubmission_penalty  + ") was provided")

    #create or edit the Exam
    if create_or_edit == "create":
        if Exam.objects.filter(course=course, slug=slug, is_deleted=False).exists():
            return HttpResponseBadRequest("An exam with this URL identifier already exists in this course")
        exam_obj = Exam(course=course, slug=slug, title=title, description=description, html_content=htmlContent, xml_metadata=metaXMLContent,
                        due_date=dd, assessment_type=assessment_type, mode="draft", total_score=total_score, grade_single=grade_single,
                        grace_period=gp, partial_credit_deadline=pcd, late_penalty=lp, submissions_permitted=sp, resubmission_penalty=rp,
                        exam_type=exam_type, autograde=autograde, display_single=display_single, invideo=invideo, section=contentsection,
                        xml_imported=xmlImported
                        )

        exam_obj.save()
        exam_obj.create_ready_instance()        

        # Set parent/child relationships
        create_contentgroup_entries_from_post(request, 'parent', exam_obj.image, 'exam', display_style='list')

        #Now set the video associations
        exam_obj.sync_videos_foreignkeys_with_metadata()
        vid_status_obj = exam_obj.image.sync_videos_foreignkeys_with_metadata()
        vid_status_string = ""
        if vid_status_obj['video_slugs_set']:
            exam_obj.invideo=True
            exam_obj.image.invideo=True
            exam_obj.save()
            exam_obj.image.save()
            vid_status_string = "This exam was successfully associated with the following videos:\n" + \
                            ", ".join(vid_status_obj['video_slugs_set']) + "\n"
        if vid_status_obj['video_slugs_not_set']:
            vid_status_string += "The following videos WERE NOT automatically associated with this exam:\n" + \
                ", ".join(vid_status_obj['video_slugs_not_set']) + "\n\n" + \
                "You may have provided the wrong url-identifier or have not yet uploaded the video"


        return HttpResponse("Exam " + title + " created. \n" + unicode(grader) + "\n\n" + vid_status_string)
    else:
        try: #this is nasty code, I know.  It should at least be moved into the model somehow
            exam_obj = Exam.objects.get(course=course, is_deleted=0, slug=old_slug)
            exam_obj.slug=slug
            exam_obj.title=title
            exam_obj.description=description
            exam_obj.html_content=htmlContent
            exam_obj.xml_metadata=metaXMLContent
            exam_obj.xml_imported=xmlImported
            exam_obj.due_date=dd
            exam_obj.total_score=total_score
            exam_obj.assessment_type=assessment_type
            exam_obj.grace_period=gp
            exam_obj.partial_credit_deadline=pcd
            exam_obj.late_penalty=lp
            exam_obj.submissions_permitted=sp
            exam_obj.resubmission_penalty=rp
            exam_obj.exam_type=exam_type
            exam_obj.autograde=autograde
            exam_obj.display_single=display_single
            exam_obj.grade_single=grade_single
            exam_obj.invideo=invideo
            exam_obj.section=contentsection
            exam_obj.save()
            exam_obj.commit()

            # Set parent/chlid relationships for this exam
            create_contentgroup_entries_from_post(request, 'parent', exam_obj.image, 'exam', display_style='list')

            #Now set the video associations
            exam_obj.sync_videos_foreignkeys_with_metadata()
            vid_status_obj = exam_obj.image.sync_videos_foreignkeys_with_metadata()
            vid_status_string = ""
            if vid_status_obj['video_slugs_set']:
                exam_obj.invideo=True
                exam_obj.image.invideo=True
                exam_obj.save()
                exam_obj.image.save()
                vid_status_string = "This exam was successfully associated with the following videos:\n" + \
                ", ".join(vid_status_obj['video_slugs_set']) + "\n\n"
            if vid_status_obj['video_slugs_not_set']:
                vid_status_string += "The following videos WERE NOT automatically associated with this exam:\n" + \
                    ", ".join(vid_status_obj['video_slugs_not_set']) + "\n" + \
                    "You may have provided the wrong url-identifier or have not yet uploaded the video"

            return HttpResponse("Exam " + title + " saved. \n" + unicode(grader) + "\n\n" + vid_status_string)

        except Exam.DoesNotExist:
            return HttpResponseBadRequest("No exam exists with URL identifier %s" % old_slug)


@require_POST
@auth_is_course_admin_view_wrapper
def check_metadata_xml(request, course_prefix, course_suffix):
    xml = request.POST.get('metaXMLContent')
    if not xml:
        return HttpResponseBadRequest("No metaXMLContent provided")
    try:
        grader = AutoGrader(xml)
    except Exception as e: #Since this is just a validator, pass back all the exceptions
        return HttpResponseBadRequest(unicode(e))
    
    videos_obj = parse_video_exam_metadata(xml)
    return HttpResponse("Metadata XML is OK.\n" + unicode(grader) + "\n" + videos_obj['description'])



@auth_is_course_admin_view_wrapper
def create_exam(request, course_prefix, course_suffix):
    
    course = request.common_page_data['course']
    
    sections = ContentSection.objects.getByCourse(course)
    
    returnURL = reverse('courses.views.course_materials',args=[course_prefix, course_suffix])
    
    return render_to_response('exams/create_exam.html', {'common_page_data':request.common_page_data,
                              'course':course,
                              'sections':sections,
                              'returnURL':returnURL},
                              RequestContext(request))

@auth_is_course_admin_view_wrapper
def edit_exam(request, course_prefix, course_suffix, exam_slug):
    
    course = request.common_page_data['course']

    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404
    
    sections = ContentSection.objects.getByCourse(course)
    returnURL = reverse('courses.views.course_materials', args=[course_prefix, course_suffix])

    data={'title':exam.title, 'slug':exam.slug, 'due_date':datetime.datetime.strftime(exam.due_date, "%m/%d/%Y %H:%M"),
          'grace_period':datetime.datetime.strftime(exam.grace_period, "%m/%d/%Y %H:%M"),
          'partial_credit_deadline':datetime.datetime.strftime(exam.partial_credit_deadline, "%m/%d/%Y %H:%M"),
          'assessment_type':exam.assessment_type, 'late_penalty':exam.late_penalty, 'num_subs_permitted':exam.submissions_permitted,
          'resubmission_penalty':exam.resubmission_penalty, 'description':exam.description, 'section':exam.section.id,'invideo':exam.invideo,
          'metadata':exam.xml_metadata, 'htmlContent':exam.html_content, 'xmlImported':exam.xml_imported}

    groupable_exam = exam
    if exam.mode != 'ready':
        groupable_exam = exam.image
    cg_info = ContentGroup.groupinfo_by_id('exam', groupable_exam.id)
    parent = cg_info.get('__parent', None)
    parent_val = "none,none"
    if parent:
        parent_val = "%s,%d" % (cg_info['__parent_tag'], parent.image.id)

    return render_to_response('exams/create_exam.html', {'common_page_data':request.common_page_data, 'returnURL':returnURL,
                                                         'course':course, 'sections':sections, 'parent_val': parent_val,
                                                         'edit_mode':True, 'prepop_json':json.dumps(data), 'slug':exam_slug,
                                                         'exam_section':exam.section, 'exam_title':exam.title, },
                                                        RequestContext(request))


def show_test_xml(request):
    return render_to_response('exams/test_xml.html', {'message':'what up G?'}, RequestContext(request))

@auth_is_course_admin_view_wrapper
def view_csv_grades(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    if course.mode=="draft":
        course = course.image

    if exam.mode=="draft":
        exam = exam.image

    # Find the appropriate ExamRecord, for each student. In this case, appropriate
    # means the last submission prior to the grace_period.
    exam_record_ptrs = ExamRecord.objects.values('student__username').filter(exam=exam, exam__grace_period__gt=F('time_created')).annotate(last_submission_id=Max('id'))
    fname = course_prefix+"-"+course_suffix+"-"+exam_slug+"-grades-"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".csv"
    outfile = open(FILE_DIR+"/"+fname,"w+")

    could_not_parse = ""

    file_content = False
    for exam_record_ptr in exam_record_ptrs:
        ers = ExamRecordScore.objects.filter(record_id=exam_record_ptr['last_submission_id'])
        
        #The ExamRecordScore will not exist for csv-graded exams if there has not been a csv grade import for this user.
        if ers:
            ersfs = ExamRecordScoreField.objects.filter(parent=ers)
        
            for ersf in ersfs:
                outstring = '"%s","%s","%s"\n' % (exam_record_ptr['student__username'], ersf.field_name, str(ersf.subscore))
                outfile.write(outstring)
                file_content = True
            
    if not file_content:
        outfile.write("\n")

    #write to S3
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    s3file = secure_file_storage.open("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname),'w')
    outfile.seek(0)
    s3file.write(outfile.read())
    s3file.close()
    outfile.close()
    return HttpResponseRedirect(secure_file_storage.url_monkeypatched("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname), response_headers={'response-content-disposition': 'attachment'}))




@require_POST
@auth_view_wrapper
def post_csv_grades(request, course_prefix, course_suffix, exam_slug):
    
    course = request.common_page_data['course']
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    #Only process ready mode exams and courses

    if course.mode == "draft":
        course = course.image
            
    if exam.mode == "draft":
        exam = exam.image

        
    good_count = 0
    exam_scores = {} #this will be the student score created
    bad_rows = []

    db_hits = 0

    if request.FILES:
        row_count=0;
        #We build up the records to be saved as a dict
        for f in request.FILES.itervalues():
            reader = csv.reader(f)
            for row in reader:  # each row should be: "<student_username>", "<field_name>", "subscore"
                row_count += 1
                valid, output = validate_row(row)
                if not valid:
                    bad_rows.append(str(row_count) + ":" + str(row) + " => " + output)
                    logger.error(str(row_count) + ":" + str(row) + " => " + output)
                else:
                    (username, field_name, score) = output
                    
                    if username in exam_scores:
                        exam_scores[username]['fields'].append({'name':field_name, 'score':score})
                        exam_scores[username]['total'] += score #increment total score
                    else:
                        exam_scores[username]={'fields':[{'name':field_name, 'score':score}], 'total':score} #initialize
                    
                    good_count += 1

                    if good_count % 100 == 0:
                        print str(good_count)

    # Find the appropriate ExamRecord, for each student, to update. In this case, appropriate
    # means the last submission prior to the grace_period.
    exam_record_ptrs = ExamRecord.objects.values('student__username').filter(exam=exam, exam__grace_period__gt=F('time_created')).annotate(last_submission_id=Max('id'))

    student_count = 0
    for username, record in exam_scores.iteritems():
        try:
            user = User.objects.get(username=username)
            user_score, created = ExamScore.objects.get_or_create(course=course, exam=exam, student=user)
            db_hits += 2
            
            #Total score for this user
            total_score = sum(map(lambda r:r['score'], record['fields']))
            if total_score != record['total']:
                bad_rows.append(username + ": total does not match sum of subscores.  Sum:" + str(total_score) + " Total:" + str(record['total']))
                logger.error(username + ": total does not match sum of subscores.  Sum:" + str(total_score) + " Total:" + str(record['total']))
            total_score = max(record['total'],0) #0 is the floor score
            
            #Find the ExamRecord for this user
            for exam_record_ptr in exam_record_ptrs:
                if exam_record_ptr['student__username'] == username:
                    break
                else:
                   exam_record_ptr = None
            
            if exam_record_ptr:
                if not created:
                    #Delete the ExamRecordScore, ExamRecordScoreFields and ExamRecordScoreFieldChoices
                    ExamRecordScoreFieldChoice.objects.filter(parent__parent__record_id=exam_record_ptr['last_submission_id']).delete()
                    ExamRecordScoreField.objects.filter(parent__record_id=exam_record_ptr['last_submission_id']).delete()
                    ExamRecordScore.objects.filter(record_id=exam_record_ptr['last_submission_id']).delete()
                    db_hits += 3
                
                #Create the new ExamRecordScore
                ers = ExamRecordScore(record_id=exam_record_ptr['last_submission_id'], raw_score=total_score, csv_imported=True)
                ers.save()
                db_hits += 1
                        
                #Create the new ExamRecordscoreFields
                field_objs = map(lambda f:ExamRecordScoreField(parent=ers, field_name=f['name'], subscore=f['score']), record['fields']) 
                ExamRecordScoreField.objects.bulk_create(field_objs)
                db_hits += 1
                                         
                #Update score for ExamRecord
                er = ExamRecord.objects.get(id=exam_record_ptr['last_submission_id'])
                er.score = total_score
                er.save()
                db_hits += 1
                                         
            #Set score for ExamScore
            user_score.score = total_score
            user_score.csv_imported = True
            user_score.save()
            db_hits += 1
        
            student_count += 1
            if student_count % 100 == 0:
                print str(student_count)
        
        except User.DoesNotExist:
            bad_rows.append(username + " not found in students list!")
            logger.error(username + " not found in students list!")

    logger.info("Good count: %d  Student count: %d  DB Hits: %d  Bad rows:%s" % (good_count, student_count, db_hits, str(bad_rows)))

    return render_to_response('exams/csv_upload_confirm.html',
                              {'common_page_data':request.common_page_data,
                               'exam':exam,
                               'good_count':good_count,
                               'db_hits':db_hits,
                               'student_count':student_count,
                               'bad_rows':bad_rows},
                              RequestContext(request))



def validate_row(row):
    """
        Helper function to validate a row read in from CSV.
        If validation fails, returns tuple of (False, error message).
        If validation succeeds, returns tuple of (True, (username, field_name, score))
    """

    if not isinstance(row, list):
        return (False, "Badly formatted row")

    if len(row) != 3:
        return  (False, "Too few or too many items in row (should be 3)")

    [username, field_name, score_str] = row
        
    if not isinstance(username, str):
        return (False, "Username is not a string")
            
    if not username:
        return (False, "Username is empty string")

    if not isinstance(field_name, str):
        return (False, "Field name is not a string")

    if not field_name:
        return (False, "Field name is empty string")

    try:
        score = float(score_str)
        if score > 10000 or score < -10000:
            return (False, "The score must be between -10000 and 10000")
    except ValueError:
        return (False, "Score cannot be converted to floating point")

    return (True, (username, field_name, score))


def log_attempt(course, exam, student, student_input, human_name, field_name, graded_obj):
    """
    ExamRecordFieldLog stores one record (row) for every attempt
    at something that can be graded problem-by-problem, currently
    interactive exercises and in-video (formative) exercises.  It
    is meant to have more info than the ExamRecord table, but to
    be useful for analytics, not scoring or reporting per se.
    """
    examLogRow = ExamRecordFieldLog(course=course,
            exam=exam, 
            student=student, 
            field_name=field_name,
            human_name=human_name, 
            value=student_input,
            raw_score=graded_obj['score'])
    examLogRow.save()


def get_or_update_incomplete_examrecord(course, exam, student):
    """Helper function that mimics get_or_update.  Creates or gets an incomplete
       examrecord for the student on exam, but deletes everything but the most
       recent if more than 1 incomplete record is found
    """
    exam_rec_queryset = ExamRecord.objects.\
    filter(course=course, exam=exam, student=student, complete=False).\
    order_by('-last_updated')   # descending by update date so first is latest

    if len(exam_rec_queryset) == 0:
        # no prior incomplete exam record found, create it
        exam_rec = ExamRecord(course=course, exam=exam, student=student, complete=False,
                              score=0.0, json_data='{}', json_score_data='{}')
    elif len(exam_rec_queryset) == 1:
        # exactly one found, this is the one we will update
        exam_rec = exam_rec_queryset[0]
    else:
        # >1 found, use the latest-updated and delete the rest. Log this as an error
        # since it is data inconsistency, even if we can clean up the mess now.
        logger.error("Found %d incomplete exam records for student=%d, exam=%d, course=%d (%s), cleaning up all but the latest-updated"
               % (len(exam_rec_queryset), student.id, exam.id, course.id, course.handle))
        exam_rec_list = list(exam_rec_queryset)
        exam_rec = exam_rec_list.pop(0)
        map(ExamRecord.delete, exam_rec_list)
    return exam_rec

def update_score(course, exam, student, student_input, field_name, graded_obj):
    """
    The ExamRecord table stores the cumulative score for this problem
    set, exercise, etc.  Update this table for things graded
    problem-by-problem (interactive exercises, in-video exercises)
    with the score for this problem.

    By convention these types of exercises are never complete, ie.
    there is never a final score.  Score here is more of a running
    tally of plus and minus points accrued.
    """
    exam_rec = get_or_update_incomplete_examrecord(course, exam, student)

    exam_rec.complete = False
    exam_rec.score = float(exam_rec.score) + float(graded_obj['score'])

    # append to json_data -- the student input
    try:
        field_student_data_obj = json.loads(exam_rec.json_data)
    except (TypeError, ValueError) as e:
        field_student_data_obj = {}  # better to ignore prior bad data than to die
    field_student_data_obj[field_name] = json.loads(student_input).get(field_name,{})
    exam_rec.json_data = json.dumps(field_student_data_obj)

    # append to json_score_data -- what the grader came back with
    try:
        field_graded_data_obj = json.loads(exam_rec.json_score_data)
    except (TypeError, ValueError) as e:
        field_graded_data_obj = {}

    # we don't want to store the whole feedback, so need to make a deep copy
    smaller_graded = copy.deepcopy(graded_obj)
    if 'feedback' in smaller_graded:
        del smaller_graded['feedback'] 
    field_graded_data_obj[field_name] = smaller_graded
    exam_rec.json_score_data = json.dumps(field_graded_data_obj)
    exam_rec.save()

    (exam_score_rec, created) = ExamRecordScore.objects.get_or_create(record=exam_rec)
    exam_score_rec.save()

 
@require_POST
@auth_view_wrapper
def exam_feedback(request, course_prefix, course_suffix, exam_slug):
    """
    This is the endpoint that will be hit from an AJAX call from
    the front-end when the users pushes the "Check Answer" button
    on an interactive or in-video exercise.  For all problems
    submitted, do three things:

      1. instantiate and call the autograder
      2. write a log entry storing the attempt
      3. update the score table with the latest score

    While this will score and report results back for multiple
    problems, that isn't typical.
    """
    course = request.common_page_data['course']
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    submissions = json.loads(request.POST['json_data'])

    autograder = None
    if exam.autograde:
        try:
            autograder = AutoGrader(exam.xml_metadata)
        except Exception as e:
            return HttpResponseBadRequest(unicode(e))
    else:
        autograder = AutoGrader("<null></null>", default_return=True) #create a null autograder that always returns the "True" object
    if not autograder:
        return Http500("Could not create autograder")

    feedback = {}
    for prob, v in submissions.iteritems():
        if prob == "__metadata__":    # shouldn't happen, being careful
            next
        try:
            if isinstance(v,list):    # multiple choice case
                student_input = map(lambda li: li['value'], v)
                feedback[prob] = autograder.grade(prob, student_input)
            else:                     # single answer case
                student_input = v['value']
                feedback[prob] = autograder.grade(prob, student_input)
        except AutoGraderGradingException as e:
            logger.error(e)
            return HttpResponse(e, status=500)
        if 'questionreport' in v:
            human_name = v['questionreport']
        else:
            human_name = ""
        log_attempt(course, exam, request.user, student_input, human_name, prob, feedback[prob])
        update_score(course, exam, request.user, request.POST.get('json_data','{}'), prob, feedback[prob])

    feedback['__metadata__'] = exam.xml_metadata if exam.xml_metadata else "<empty></empty>"
    return HttpResponse(json.dumps(feedback))

@require_POST
@auth_view_wrapper
def student_save_progress(request, course_prefix, course_suffix, exam_slug):
    """This is the endpoint for the "Save" button in the exam.  It just
       saves what they did, without any grading activity
    """
    course = request.common_page_data['course']
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    exam_rec = get_or_update_incomplete_examrecord(course, exam, request.user)
    exam_rec.json_data = request.POST.get('json_data',"{}")
    exam_rec.save()
    return HttpResponse("OK")

