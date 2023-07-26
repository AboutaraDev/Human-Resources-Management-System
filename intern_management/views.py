from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import CustomUser
from intern_management.EmailBackEnd import EmailBackEnd

# Create your views here.
from django.utils.translation import gettext_lazy as _


def loginPage(request):
    return render(request, 'login.html')



def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>_(Method Not Allowed)</h2>")
    else:
        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            user_type = user.user_type
            #return HttpResponse("Email: "+request.POST.get('email')+ " Password: "+request.POST.get('password'))
            if user_type == CustomUser.HOD:
                return redirect('admin_home')
                
            elif user_type == CustomUser.STAFF:
                # return HttpResponse("Staff Login")
                return redirect('staff_home')
                
            elif user_type == CustomUser.INTERN:
                # return HttpResponse("Student Login")
                return redirect('intern_home')
            else:
                messages.error(request, _("Invalid Login!"))
                return redirect('login')
        else:
            messages.error(request, _("Invalid Login Credentials!"))
            #return HttpResponseRedirect("/")
            return redirect('login')


def get_user_details(request):
    if request.user != None:
        return HttpResponse("User: "+request.user.email+" User Type: "+request.user.user_type)
    else:
        return HttpResponse(_("Please Login First"))



def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')




