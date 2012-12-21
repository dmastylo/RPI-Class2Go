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
from django.db.models import Sum
import urllib2, urlparse
from xml.dom.minidom import parseString


FILE_DIR = getattr(settings, 'FILE_UPLOAD_TEMP_DIR', '/tmp')
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
AWS_SECURE_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_SECURE_STORAGE_BUCKET_NAME', '')

logger = logging.getLogger(__name__)

from c2g.models import ContentGroup, Exercise, Video, VideoToExercise, ProblemSet, ProblemSetToExercise, Exam, ExamRecord, ExamScore, ExamScoreField, ExamRecordScore, ExamRecordScoreField, ExamRecordScoreFieldChoice, ContentSection
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from django.core.validators import validate_slug, ValidationError
from django.core.exceptions import MultipleObjectsReturned
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
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


# Create your views here.
@auth_view_wrapper
def show_exam(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    too_many_attempts = exam.max_attempts_exceeded(request.user)
    
    #self.metadata_xml = xml #The XML metadata for the entire problem set.
    metadata_dom = parseString(exam.xml_metadata) #The DOM corresponding to the XML metadata
    questions = metadata_dom.getElementsByTagName('video')

    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'json_pre_pop':"{}",
                              'scores':"{}",'editable':True,'single_question':exam.display_single,'videotest':False,
                              'allow_submit':True, 'too_many_attempts':too_many_attempts,
                              'exam':exam, 'question_times':exam.xml_metadata}, RequestContext(request))

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


    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop,
                                                       'json_pre_pop_correx':json_pre_pop_correx, 'scores':scores, 'editable':editable,
                                                       'allow_submit':True, 'too_many_attempts':too_many_attempts},
                              RequestContext(request))

@require_POST
@auth_view_wrapper
def show_quick_check(request, course_prefix, course_suffix, exam_slug):
    course = request.common_page_data['course']
    parser = HTMLParser.HTMLParser()
    user_answer_data = parser.unescape(request.POST['user-answer-data'])
 
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    return render_to_response('exams/quickcheck.html', {'common_page_data':request.common_page_data, 'exam':exam, 'user_answer_data':user_answer_data, 'videotest':True}, RequestContext(request))

def show_invideo_quiz(request, course_prefix, course_suffix, exam_slug):
    return render_to_response('exams/videotest.html', {'common_page_data':request.common_page_data}, RequestContext(request))

@auth_view_wrapper
def show_graded_exam(request, course_prefix, course_suffix, exam_slug, type="exam"):
    course = request.common_page_data['course']
    
    try:
        exam = Exam.objects.get(course=course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    try:
        record = ExamRecord.objects.filter(course=course, exam=exam, student=request.user, complete=True, time_created__lt=exam.grace_period).latest('time_created')
        json_pre_pop = record.json_data
        if record.json_score_data:
            correx_obj = json.loads(record.json_score_data)
        else:
            correx_obj = {}
        correx_obj['__metadata__'] = exam.xml_metadata if exam.xml_metadata else "<empty></empty>"
        json_pre_pop_correx = json.dumps(correx_obj)
        
    except ExamRecord.DoesNotExist:
        record = None
        json_pre_pop = "{}"
        json_pre_pop_correx = "{}"

    try:
        score_obj = ExamScore.objects.get(course=course, exam=exam, student=request.user)
        score = score_obj.score
        score_fields = {}
        for s in list(ExamScoreField.objects.filter(parent=score_obj)):
            score_fields[s.field_name] = s.subscore
        scores_json = json.dumps(score_fields)
    except ExamScore.DoesNotExist, ExamScore.MultipleObjectsReturned:
        score = None
        score_fields = {}
        scores_json = "{}"

    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop, 'scores':scores_json, 'json_pre_pop_correx':json_pre_pop_correx, 'editable':False, 'score':score, 'allow_submit':False}, RequestContext(request))


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

    except ExamRecordScore.DoesNotExist, ExamScore.MultipleObjectsReturned:
        raw_score = None
        scores_json = "{}"


    
    return render_to_response('exams/view_exam.html', {'common_page_data':request.common_page_data, 'exam':exam, 'json_pre_pop':json_pre_pop, 'scores':scores_json, 'score':score, 'json_pre_pop_correx':json_pre_pop_correx, 'editable':False, 'raw_score':raw_score, 'allow_submit':False}, RequestContext(request))




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
    fname = course_prefix+"-"+course_suffix+"-"+exam_slug+"-"+datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+".csv"
    outfile = open(FILE_DIR+"/"+fname,"w+")

    could_not_parse = ""

    for s in submitters: #yes, there is sql in a loop here.  We'll optimize later
        latest_sub = ExamRecord.objects.values('student__username', 'time_created', 'json_data').filter(exam=exam, time_created__lt=exam.grace_period, student=s['student']).latest('time_created')
        try:
            sub_obj = json.loads(latest_sub['json_data']).iteritems()
            for k,v in sub_obj:
                outstring = '"%s","%s","%s"\n' % (latest_sub['student__username'], k, parse_val(v))
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
    elif isinstance(v,basestring):
        return v
    else:
        try:
           return(v['value'])
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

    if exam.past_all_deadlines():
        return HttpResponseBadRequest("Sorry!  This submission is past the last deadline of %s" % \
                                      datetime.datetime.strftime(exam.partial_credit_deadline, "%m/%d/%Y %H:%M PST"));

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
                                                     value = submission,
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
        
        #apply resubmission penalty
        resubmission_penalty_percent = pow(((100 - exam.resubmission_penalty)/100), (attempt_number -1))
        total_score = max(total_score * resubmission_penalty_percent, 0)
        
        #apply the late penalty
        if exam.grace_period and exam.late_penalty > 0 and datetime.datetime.now() > exam.grace_period:
            total_score = max(total_score * ((100 - exam.late_penalty)/100), 0)
        
        record.score = total_score
        record.save()
        
        #Set ExamScore.score to max of ExamRecord.score for that student, exam. 
        exam_score, created = ExamScore.objects.get_or_create(course=course, exam=exam, student=user)
        exam_score.setScore()

        return HttpResponse(reverse(exam.record_view, args=[course.prefix, course.suffix, exam.slug, record.id]))

    else:
        return HttpResponse("Submission has been saved.")


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
    parent=request.POST.get('parent','none,none')
    
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

    if parent and parent[:4] != 'none':
        parent_type, parent = parent.split(',')
    else:
        parent_type, parent = None, None

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

        if parent_type:
            parent_ref = ContentGroup.groupable_types[parent_type].objects.get(id=long(parent)).image
            content_group_groupid = ContentGroup.add_parent(exam_obj.image.course, parent_type, parent_ref.image)
            ContentGroup.add_child(content_group_groupid, 'exam', exam_obj.image, display_style='list')

        return HttpResponse("Exam " + title + " created. \n" + unicode(grader))
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

            if parent_type:
                parent_ref = ContentGroup.groupable_types[parent_type].objects.get(id=long(parent)).image
                content_group_parent = parent_ref.contentgroup_set.all()
                if content_group_parent:
                    content_group_groupid = content_group_parent[0].group_id
                else:
                    content_group_groupid = ContentGroup.add_parent(exam_obj.image.course, parent_type, parent_ref.image)
                ContentGroup.add_child(content_group_groupid, 'exam', exam_obj.image, display_style='list')

            return HttpResponse("Exam " + title + " saved. \n" + unicode(grader))

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
    
    return HttpResponse("Metadata XML is OK.\n" + unicode(grader))



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

    return render_to_response('exams/create_exam.html', {'common_page_data':request.common_page_data, 'returnURL':returnURL,
                                                         'course':course, 'sections':sections,
                                                         'edit_mode':True, 'prepop_json':json.dumps(data), 'slug':exam_slug },
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
    
    graded_students = ExamScore.objects.filter(course=course, exam=exam).values('student','student__username').distinct()
    fname = course_prefix+"-"+course_suffix+"-"+exam_slug+"-grades-"+datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+".csv"
    outfile = open(FILE_DIR+"/"+fname,"w+")

    could_not_parse = ""

    for s in graded_students: #yes, there is sql in a loop here.  We'll optimize later
        #print(s)
        score_obj = ExamScore.objects.get(course=course, exam=exam, student=s['student'])
        subscores = ExamScoreField.objects.filter(parent=score_obj)
        for field in subscores:
            outstring = '"%s","%s","%s"\n' % (s['student__username'], field.field_name, str(field.subscore))
            outfile.write(outstring)

    outfile.write("\n")

    #write to S3
    secure_file_storage = S3BotoStorage(bucket=AWS_SECURE_STORAGE_BUCKET_NAME, access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)
    s3file = secure_file_storage.open("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname),'w')
    outfile.seek(0)
    s3file.write(outfile.read())
    s3file.close()
    outfile.close()
    return HttpResponseRedirect(secure_file_storage.url("/%s/%s/reports/exams/%s" % (course_prefix, course_suffix, fname), response_headers={'response-content-disposition': 'attachment'}))




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

    student_count = 0
    for username, record in exam_scores.iteritems():
        try:
            user = User.objects.get(username=username)
            user_score, created = ExamScore.objects.get_or_create(course=course, exam=exam, student=user)
            db_hits += 2
            
            if not created:
                #yes, we delete them all to start.  Uploading a CSV replaces the grades for this student on this exam
                #we do this to allow batched SQL later
                ExamScoreField.objects.filter(parent=user_score).delete()
                db_hits += 1
            
            field_objs = map(lambda f:ExamScoreField(parent=user_score, field_name=f['name'], subscore=f['score']), record['fields'])
            ExamScoreField.objects.bulk_create(field_objs)
            db_hits += 1

            total_1 = sum(map(lambda r:r['score'], record['fields']))
            if total_1 != record['total']:
                bad_rows.append(username + ": total does not match sum of subscores.  Sum:" + str(total_1) + " Total:" + str(record['total']))
                logger.error(username + ": total does not match sum of subscores.  Sum:" + str(total_1) + " Total:" + str(record['total']))
            user_score.score = max(record['total'],0) #0 is the floor score
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
        score = int(score_str)
        if score > 10000 or score < -10000:
            return (False, "The score must be between -10000 and 10000")
    except ValueError:
        return (False, "Score cannot be converted to integer")

    return (True, (username, field_name, score))




# Test values for interactive exercises
canned_feedback = {}
canned_feedback['wrong'] = r'{"score":0,"maximum-score":1,"feedback":[{"user_answer":"select * from movie","score":0,"explanation":" <br><font style=\"color:red; font-weight:bold;\">Incorrect<\/font><br><br>Your Query Result: <table border=\"1\" style=\"font-size:90%; padding: 1px;border-spacing: 0px; border-collapse: separate\"><tr><td>101<\/td><td>Gone with the Wind<\/td><td>1939<\/td><td>Victor Fleming<\/td><\/tr><tr><td>102<\/td><td>Star Wars<\/td><td>1977<\/td><td>George Lucas<\/td><\/tr><tr><td>103<\/td><td>The Sound of Music<\/td><td>1965<\/td><td>Robert Wise<\/td><\/tr><tr><td>104<\/td><td>E.T.<\/td><td>1982<\/td><td>Steven Spielberg<\/td><\/tr><tr><td>105<\/td><td>Titanic<\/td><td>1997<\/td><td>James Cameron<\/td><\/tr><tr><td>106<\/td><td>Snow White<\/td><td>1937<\/td><td>&lt;NULL&gt;<\/td><\/tr><tr><td>107<\/td><td>Avatar<\/td><td>2009<\/td><td>James Cameron<\/td><\/tr><tr><td>108<\/td><td>Raiders of the Lost Ark<\/td><td>1981<\/td><td>Steven Spielberg<\/td><\/tr><\/table> <br>Expected Query Result: <table border=\"1\" style=\"font-size:90%; padding: 1px;border-spacing: 0px; border-collapse: separate\"><tr><td>E.T.<\/td><\/tr><tr><td>Raiders of the Lost Ark<\/td><\/tr><\/table>"}]}'
canned_feedback['correct'] = r'{"score":1,"maximum-score":1,"feedback":[{"user_answer":"select title from movie where director=\"Steven Spielberg\";","score":1,"explanation":" <br><font style=\"color:green; font-weight:bold;\">Correct<\/font><br><br>Your Query Result: <table border=\"1\" style=\"font-size:90%; padding: 1px;border-spacing: 0px; border-collapse: separate\"><tr><td>E.T.<\/td><\/tr><tr><td>Raiders of the Lost Ark<\/td><\/tr><\/table> <br>Expected Query Result: <table border=\"1\" style=\"font-size:90%; padding: 1px;border-spacing: 0px; border-collapse: separate\"><tr><td>E.T.<\/td><\/tr><tr><td>Raiders of the Lost Ark<\/td><\/tr><\/table>"}]}'
canned_feedback['right'] = canned_feedback['correct']
canned_feedback['help'] = r'{"score":0,"maximum-score":1,"feedback":[{"user_answer":"help","score":0,"explanation":"You are in localhost debugging mode.<br>Try \"<tt>right</tt>\" or \"<tt>wrong</tt>\""}]}'
canned_feedback['error'] = r'{"score":0,"maximum-score":1,"feedback":[{"user_answer":"error","score":0,"explanation":"You are in localhost debugging mode.<br>Did not send a well-formatted request."}]}'


def save_feedback(course, exam, student, student_input, field_name, graded_obj):
    (exam_rec, created) = ExamRecord.objects.get_or_create(course=course, exam=exam, student=student)

    exam_rec.complete = False
    exam_rec.score = 0
    exam_rec.attempt_number += 1

    # append to json_data -- the student input
    try:
        field_student_data_obj = json.loads(exam_rec.json_data)
    except:
        field_student_data_obj = {}
    field_student_data_obj[field_name] = {'value': student_input}
    exam_rec.json_data = json.dumps(field_student_data_obj)

    # append to json_score_data -- what the grader came back with
    try:
        field_graded_data_obj = json.loads(exam_rec.json_score_data)
    except:
        field_graded_data_obj = {}
    field_graded_data_obj[field_name] = graded_obj
    exam_rec.json_score_data = json.dumps(field_graded_data_obj)

    exam_rec.save()

    (exam_score_rec, created) = ExamRecordScore.objects.get_or_create(record=exam_rec)
    exam_score_rec.save()


@require_POST
@auth_view_wrapper
def interactive_exercise_feedback(request, course_prefix, course_suffix, exam_slug):
    """
    Proxies request to the exercise grader so we can both handle the request
    without CORS, and (more importantly) store the answer for later.

    Expects the ID of the question to be in a query parameter
    """
    course = request.common_page_data['course']
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    # the question ID is in the query string, "unknown" if not provided
    qid = request.GET.get('id', 'unknown')

    grader_hostname = getattr(settings, 'GRADER_ENDPOINT', 'localhost')
    try:
        parsed_body=urlparse.parse_qs(request.body)
        student_input=parsed_body['student_input'][0]
    except:
        student_input='error'

    if grader_hostname == 'localhost':
        graded_raw = canned_feedback['help']
        if student_input in canned_feedback.keys():
            graded_raw = canned_feedback[student_input]
    else:
        grader_url = "http://%s/AJAXPostHandler.php" % grader_hostname
        grader_data = request.body
        grader_timeout = 5    # seconds
        try:
            response = urllib2.urlopen(grader_url, grader_data, grader_timeout)
        except urllib2.URLError, e:
            return HttpResponse("Error in the interactive grader backend, please try again later.",
                    status=500)
        graded_raw = response.read()

    graded_obj=json.loads(graded_raw)
    save_feedback(course, exam, request.user, student_input, qid, graded_obj)

    response = HttpResponse(graded_raw)
    return response

    
@require_POST
@auth_view_wrapper
def invideo_feedback(request, course_prefix, course_suffix, exam_slug):
    """
    Store results from invideo formative exams.  Problem ID in "id" query param.
    """
    course = request.common_page_data['course']
    try:
        exam = Exam.objects.get(course = course, is_deleted=0, slug=exam_slug)
    except Exam.DoesNotExist:
        raise Http404

    # the question ID is in the query string, "unknown" if not provided
    qid = request.GET.get('id', 'unknown')

    # TODO -- video 
    save_feedback(course, exam, request.user, request.body, qid, 'result')

    response = HttpResponse()  # TODO -- return anything?
    return response

