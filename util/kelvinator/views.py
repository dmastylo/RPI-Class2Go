from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response
from forms import ExtractForm
import kelvinator

def healthcheck(request):
    return HttpResponse("I'm alive!")

def nobodyhome(request):
    return render_to_response('nobodyhome.html')

def extract(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ExtractForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            kelvinator.run(form.cleaned_data)
            return HttpResponseRedirect('/extract') # Redirect after POST
    else:
        form = ExtractForm() # An unbound form

    return render(request, 
                  'extract.html', 
                  {'form': form}
            ) 


