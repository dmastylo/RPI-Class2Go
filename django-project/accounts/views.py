# Create your views here.
from django.http import HttpResponse
from django.contrib.auth import logout
from django.shortcuts import redirect

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")

def profile(request):
	return redirect('c2g.views.home')
	
def logout(request):
	logout(request)
	return redirect('c2g.views.home')