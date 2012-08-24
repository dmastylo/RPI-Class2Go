from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext

from c2g.models import Video
from courses.actions import auth_view_wrapper

@auth_view_wrapper
def view(request, course_prefix, course_suffix, video_id):
    video = Video.objects.get(id=video_id)
    return render_to_response('video_exercises/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'video': video, 'request': request}, context_instance=RequestContext(request))
