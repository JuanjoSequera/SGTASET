from django.shortcuts import render, redirect

# Create your views here.

def inicio(request): 
	if request.user.is_authenticated:
		return render (request, 'home.html')
	else:
		return redirect('login')

