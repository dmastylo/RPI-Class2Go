from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from django.contrib.auth.models import User,Group
from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from courses.forms import *
from c2g.models import *
from random import randrange
from datetime import datetime

from django.utils.functional import wraps

def auth_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        user = request.user
        course = request.common_page_data['course']

        if user.is_authenticated() and not is_member_of_course(course, user):
            messages.add_message(request,messages.ERROR, 'You must be a member of the course to view the content you chose.')      
            return HttpResponseRedirect(reverse('courses.views.main', args=(request.common_page_data['course_prefix'], request.common_page_data['course_suffix'],)))

        if not user.is_authenticated():
            messages.add_message(request,messages.ERROR, 'You must be logged-in to view the content you chose.')

            return HttpResponseRedirect(reverse('courses.views.main', args=(request.common_page_data['course_prefix'], request.common_page_data['course_suffix'],)))

        return view(request, *args, **kw)
    return inner

def auth_can_switch_mode_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        if request.common_page_data['can_switch_mode']:
            return view(request, *args, **kw)
        else:
            messages.add_message(request,messages.ERROR, "You don't have permission to view that content.")
            return HttpResponseRedirect(reverse('courses.views.main', args=(request.common_page_data['course_prefix'], request.common_page_data['course_suffix'],)))
    return inner

def auth_is_course_admin_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        if request.common_page_data['is_course_admin']:
            return view(request, *args, **kw)
        else:
            messages.add_message(request,messages.ERROR, "You don't have permission to view that content.")
            return HttpResponseRedirect(reverse('courses.views.main', args=(request.common_page_data['course_prefix'], request.common_page_data['course_suffix'],)))
    return inner

def auth_is_staff_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        user = request.user
        if user.is_staff:
            return view(request, *args, **kw)
        else:
           raise Http404
    return inner                

@require_POST
@auth_can_switch_mode_view_wrapper
def switch_mode(request):
    
    common_page_data = request.common_page_data
    request.session['course_mode'] = request.POST.get('to_mode')
    return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def add_section(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = request.common_page_data

    index = len(ContentSection.objects.filter(course=common_page_data['course']))

    draft_section = ContentSection(course=common_page_data['draft_course'], title=request.POST.get("title"), index=index, mode='draft')
    draft_section.save()

    draft_section.create_ready_instance()

    return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def commit(request):
    ids = request.POST.get("commit_ids").split(",")
    for id in ids:
        parts = id.split('_')
        if parts[0] == 'video':
            Video.objects.get(id=parts[1]).commit()
        elif parts[0] == 'problemset':
            ProblemSet.objects.get(id=parts[1]).commit()
        elif parts[0] == 'additionalpage':
            AdditionalPage.objects.get(id=parts[1]).commit()
    return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def revert(request):
    ids = request.POST.get("revert_ids").split(",")
    for id in ids:
        parts = id.split('_')
        if parts[0] == 'video':
            Video.objects.get(id=parts[1]).revert()
        elif parts[0] == 'problemset':
            ProblemSet.objects.get(id=parts[1]).revert()
        elif parts[0] == 'additionalpage':
            AdditionalPage.objects.get(id=parts[1]).revert()
    return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def change_live_datetime(request):
    list_type = request.POST.get('list_type')
    action = request.POST.get('action')
    form = LiveDateForm(request.POST)
    if form.is_valid():
        if action == "Make Ready and Go Live":
            new_live_datetime = datetime.now()
        elif action == "Set Live Date":
            new_live_datetime = form.cleaned_data['live_datetime']
        else:
            new_live_datetime = None

        ids = request.POST.get("change_live_datetime_ids").split(",")

        for id in ids:
            parts = id.split('_')
            if parts[0] == 'video':
                content = Video.objects.get(id=parts[1])
            elif parts[0] == 'problemset':
                content = ProblemSet.objects.get(id=parts[1])
            elif parts[0] == 'additionalpage':
                content = AdditionalPage.objects.get(id=parts[1])
            elif parts[0] == 'file':
                content = File.objects.get(id=parts[1])

            if action == "Make Ready and Go Live" and parts[0] != 'file':
                content.commit()
            content.live_datetime = new_live_datetime
            content.image.live_datetime = new_live_datetime
            content.save()
            content.image.save()

        if list_type == 'course_materials':
            return redirect('courses.views.course_materials', request.common_page_data['course_prefix'], request.common_page_data['course_suffix'])
        elif list_type == 'problemsets':
            return redirect('problemsets.views.list', request.common_page_data['course_prefix'], request.common_page_data['course_suffix'])
        else:
            return redirect('courses.videos.views.list', request.common_page_data['course_prefix'], request.common_page_data['course_suffix'])
        #This won't work anymore because referer could be /change_live_datetime if it's an invalid form post
        #return redirect(request.META['HTTP_REFERER'])

    if list_type == 'course_materials':
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True, get_pset_content=True, get_additional_page_content=True, get_file_content=True)
        template = 'courses/draft/course_materials.html'
    elif list_type == 'problemsets':
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_pset_content=True)
        template = 'problemsets/draft/list.html'
    else:
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True)
        template = 'videos/draft/list.html'
    return render(request, template,
                  {'common_page_data': request.common_page_data,
                   'section_structures': section_structures,
                   'form': form})

def is_member_of_course(course, user):
    student_group_id = course.student_group.id
    instructor_group_id = course.instructor_group.id
    tas_group_id = course.tas_group.id
    readonly_tas_group_id = course.readonly_tas_group.id

    group_list = user.groups.values_list('id',flat=True)

    for item in group_list:
        if item == student_group_id or item == instructor_group_id or item == tas_group_id or item == readonly_tas_group_id:
            return True

    return False


@require_POST
@csrf_protect
def signup_with_course(request, course_prefix, course_suffix):
    course = request.common_page_data['course']
    if course.institution_only and (course.institution not in request.user.get_profile().institutions.all()):
        messages.add_message(request,messages.ERROR, 'Registration in this course is restricted to ' + course.institution.title + '.  Perhaps you need to logout and login with your '+ course.institution.title + ' credentials?')
        return redirect(reverse('courses.views.main',args=[course_prefix,course_suffix]))

    if not is_member_of_course(course, request.user):
        student_group = Group.objects.get(id=course.student_group_id)
        student_group.user_set.add(request.user)
    if (request.GET.__contains__('redirect_to')):
            return redirect(request.GET.get('redirect_to'))
    return redirect(reverse('courses.views.main',args=[course_prefix,course_suffix]))


@require_POST
def signup(request):
    handle = request.POST.get('handle')

    user = request.user
    course = Course.objects.get(handle=handle, mode = "ready")
    if not is_member_of_course(course, user):
        student_group = Group.objects.get(id=course.student_group_id)
        student_group.user_set.add(user)

    return redirect(request.META['HTTP_REFERER'])



