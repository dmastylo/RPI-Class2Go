from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import Course, Announcement, NewsEvent
import re

def all(request):
	course_list = Course.objects.select_related('institution').all()
	return render_to_response('courses/all.html', {'request': request, 'course_list': course_list}, context_instance=RequestContext(request))
	
def current(request):
	return render_to_response('courses/current.html', {'request': request}, context_instance=RequestContext(request))
	
def mine(request):
	return render_to_response('courses/mine.html', {'request': request}, context_instance=RequestContext(request))
	
def view(request, course_prefix, course_suffix):
	try:
		course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
	except:
		raise Http404
	
	f = open("C:/c2g_filestore/"+course_prefix+"-"+course_suffix+"/production/homepage_middle_column.html","r")
	m_content = f.read();
	f.close()
	
	announcement_div_matches = re.search(r'<div\s+class\s*=\s*[\'"]announcements[\'"]\s*/>', m_content)
	if len(announcement_div_matches) > 0:
		announcement_list = course.announcement_set.all().order_by('-time_created')
		announcements_html = "<div><h3>Announcements</h3>"
		if len(announcement_list) == 0:
			announcements_html += "<h4>No announcements to show.</h4>"
		for announcement in announcement_list:
			announcements_html += "<h4>"+announcement.title+"</h4><p>"+announcement.description+'</p><p align="right">By '+announcement.owner.first_name+" "+announcement.owner.last_name+"</p>"
		announcements_html += "</div>";
		
		m_content = re.sub(r'<div\s+class\s*=\s*[\'"]announcements[\'"]\s*/>', announcements_html, m_content)
	
	f = open("C:/c2g_filestore/"+course_prefix+"-"+course_suffix+"/production/homepage_right_column.html","r")
	r_content = f.read();
	f.close()
	
	news_list_div_matches = re.search(r'<div\s+class\s*=\s*[\'"]news_list[\'"]\s*/>', r_content)
	if len(news_list_div_matches) > 0:
		news_list = course.newsevent_set.all().order_by('-time_created')[0:5]
		news_list_html = "<div><h3>News List</h3>"
		if len(news_list) == 0:
			news_list_html += "No news events to display"
		else:
			for news_item in news_list:
				news_list_html += news_item.time_created + " - " + news_item.event + "<br/><br/>"
		news_list_html += "</div>"
		
		r_content = re.sub(r'<div\s+class\s*=\s*[\'"]news_list[\'"]\s*/>', news_list_html, r_content)
	
	return render_to_response('courses/view.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'm_content': m_content, 'r_content': r_content, 'request': request}, context_instance=RequestContext(request))

def description(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    
    f = open("C:/c2g_filestore/"+course_prefix+"-"+course_suffix+"/production/course_info/course_description.html","r")
    content = f.read();
    f.close()

    return render_to_response('courses/description.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'content': content, 'request': request}, context_instance=RequestContext(request))
	
def syllabus(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    
    f = open("C:/c2g_filestore/"+course_prefix+"-"+course_suffix+"/production/course_info/syllabus.html","r")
    content = f.read();
    f.close()

    return render_to_response('courses/syllabus.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'content': content, 'request': request}, context_instance=RequestContext(request))

def prereqs(request, course_prefix, course_suffix):
    try:
        course = Course.objects.get(handle=course_prefix+"-"+course_suffix)
    except:
        raise Http404
    
    f = open("C:/c2g_filestore/"+course_prefix+"-"+course_suffix+"/production/course_info/prerequisites.html","r")
    content = f.read();
    f.close()
	
    return render_to_response('courses/prereqs.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'course': course, 'content': content, 'request': request}, context_instance=RequestContext(request))
