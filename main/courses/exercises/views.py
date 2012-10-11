# Create your views here.
import sys
import traceback
import logging
logger = logging.getLogger(__name__)

from c2g.models import Exercise, Video, VideoToExercise, ProblemSet, ProblemSetToExercise
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from django.core.exceptions import MultipleObjectsReturned 
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse

from django.views.decorators.csrf import csrf_protect

def edit(request, course_prefix, course_suffix, filename):
    course = request.common_page_data['course']
    handle = course_prefix+'--'+course_suffix
    try:
        exercise = Exercise.objects.get(handle=handle, fileName=filename)
    except Exercise.DoesNotExist:
        raise Http404("This exercise does not exist")
    #not catching MultipleObjectsReturned because that indicates db integrity issues and should get through as a 500

    if request.GET['return']:
        returnurl = request.GET['return']
    else:
        returnurl = reverse('courses.views.course_materials', args=[course_prefix,course_suffix])
    return render_to_response('exercises/edit.html',
                              {'common_page_data':request.common_page_data,
                              'filename':filename,
                              'returnURL':returnurl,
                              'file_content':exercise.file.read(),},
                              RequestContext(request))

@auth_is_course_admin_view_wrapper
@require_POST
@csrf_protect
def save(request, course_prefix, course_suffix, filename):
    course = request.common_page_data['course']
    handle = course_prefix+'--'+course_suffix
    try:
        exercise = Exercise.objects.get(handle=handle, fileName=filename)
    except Exercise.DoesNotExist:
        raise Http404("This exercise does not exist")
    #not catching MultipleObjectsReturned because that indicates db integrity issues and should get through as a 500

    try:
       newfile = default_storage.open(exercise.file.name,'rw+')
       newfile.seek(0)
       newfile.write(request.POST['content'].encode('utf-8'))
       newfile.truncate()
       newfile.close()
       exercise.file.save(filename, newfile)
    except BaseException as e:
        #yes, we're catching all exceptions, but this is for the purpose of sending back an understandable
        #ajax error message.  We'll log the exception which causes email to be sent
        type, value = sys.exc_info()[:2] #per http://docs.python.org/library/sys.html#sys.exc_info
        logger.exception(str(type)+str(value))
        return HttpResponseBadRequest(unicode(e))

    return HttpResponse(exercise.file.name)