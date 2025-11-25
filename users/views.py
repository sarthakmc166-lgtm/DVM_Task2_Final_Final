from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from ticket.models import SystemToggle


def signup_view(request):
    system = SystemToggle.objects.first()
    status = system.status
    if status == True :
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            # Additional fields can be captured here

            if not username or not password:
                messages.error(request, "Username and password are required.")
            else:
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already taken.")
                else:
                    user = User.objects.create_user(username=username, password=password)
                    user.save()
                    messages.success(request, "Signup successful. Please log in.")
                    return redirect('login')
        return render(request, "users/signup.html")
    else :
        return render(request, 'ticket/down.html')

def login_view(request):
    system = SystemToggle.objects.first()
    status = system.status
    if status == True :
        if request.method == "POST":   
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None and not user.is_staff:
                login(request, user)
                return redirect('menu') 
            else:
                messages.error(request, "Invalid passenger credentials.")
                return redirect('signup')
        return render(request, "users/login.html")
    else :
        return render(request, 'ticket/down.html')
  
def logout_view(request):
    logout(request)
    return render(request, "users/landing_page.html") #enter the redirect url

def landing_page_view(request):
    if request.method == "POST" :
        choice = request.POST.get('choice')
        if choice == "custom" :
            return render(request, "users/login.html")
        elif choice == "google" :
            pass
        elif choice == "signup" :
            return render(request, "users/signup.html")
    return render(request, 'users/landing_page.html')

def post_login(request) :
    if request.user.is_authenticated and request.user.is_superuser :
        return redirect('admin-menu')
    if request.user.is_authenticated and request.user.is_staff :
        return render(request, 'ticket/staff_menu.html')
    if request.user.is_authenticated and not request.user.is_staff :
        return redirect ('menu')
    
def staff_login() :
    pass
            


