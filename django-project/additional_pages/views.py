from django.http import HttpResponse

def list(request, course_id=-1):
    return HttpResponse("This is the additional pages list.")

def show(request, additional_page_id=-1):
    return HttpResponse("This shows the additional pages.")
