from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response
from forms import ExtractForm
import tasks

def extract(request):
    if request.method == 'POST':         # If the form has been submitted...
        form = ExtractForm(request.POST) # A form bound to the POST data
        if form.is_valid():              # All validation rules pass
            tasks.run("s3://%(bucket)s%(path)s" % form.cleaned_data,
                      form.cleaned_data['frames'],
                      form.cleaned_data['threshold'])
            return HttpResponseRedirect('/extract') # Redirect after POST

    else:
        form = ExtractForm() # An unbound form

    return render(request, 'extract.html', {'form': form}) 

