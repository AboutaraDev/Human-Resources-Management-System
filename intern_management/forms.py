from django import forms 
from .models import Department, SessionYearModel, Service

from django.utils.translation import gettext_lazy as _





class DateInput(forms.DateInput):
    input_type = "date"


class AddInternForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label=_("Password"), max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control", "name":"password"}))
    first_name = forms.CharField(label=_("First Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control", "name":"first_name"}))
    last_name = forms.CharField(label=_("Last Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control", "name":"last_name"}))
    username = forms.CharField(label=_("Username"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control", "name":"username"}))
    address = forms.CharField(label=_("Address"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control", "name":"address"}))

    #For Displaying Departments
    try:
        departments = Department.objects.all()
        department_list = []
        for department in departments:
            deptName = _(department.department_name)
            single_department = (department.id, deptName)
            department_list.append(single_department)
        
        
    except:
        department_list = []
    
    print(department_list)
    #For Displaying Departments
    try:
        services = Service.objects.all()
        service_list = []
        for service in services:
            servName = _(service.service_name)
            single_service = (service.id, servName)
            service_list.append(single_service)
        
        
    except:
        service_list = []
    
    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        
        for session_year in session_years:
            
            session_text = f"{str(session_year.session_start_year)} - {str(session_year.session_end_year)}"
            single_session_year = (session_year.id, session_text)
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []
    
    gender_list = (
        ('Male',_('Male')),
        ('Female',_('Female'))
    )
    
    department_id = forms.ChoiceField(label=_("Department"), choices=department_list, widget=forms.Select(attrs={"class":"form-control", "id": "department_id", "name": "department_id"}))
    service_id = forms.ChoiceField(label=_("Service"), choices=service_list, widget=forms.Select(attrs={"class":"form-control", "id": "service_id", "name": "service_id"}))
    gender = forms.ChoiceField(label=_("Gender"), choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    num_tel = forms.CharField(label=_("Phone Number"), widget=forms.TextInput(attrs={"class":"form-control", "placeholder": _("Enter your phone number")}))
    session_year_id = forms.ChoiceField(label=_("Assignment Period"), choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))

    profile_pic = forms.FileField(label=_("Profile Pic"), required=False, widget=forms.FileInput(attrs={"class":"form-control"}))



class EditInternForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label=_("First Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control arabic-input"}))
    last_name = forms.CharField(label=_("Last Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control arabic-input"}))
    username = forms.CharField(label=_("Username"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control arabic-input"}))
    address = forms.CharField(label=_("Address"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control arabic-input"}))

    #For Displaying Departments
    try:
        departments = Department.objects.all()
        department_list = []
        for department in departments:
            single_department = (department.id, department.department_name)
            department_list.append(single_department)
    except:
        department_list = []
    
    #For Displaying Departments
    try:
        services = Service.objects.all()
        service_list = []
        for service in services:
            servName = _(service.service_name)
            single_service = (service.id, servName)
            service_list.append(single_service)
        
        
    except:
        service_list = []

    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            
            session_text = f"{str(session_year.session_start_year)} - {str(session_year.session_end_year)}"
            single_session_year = (session_year.id, session_text)
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []

    
    gender_list = (
        ('Male',_('Male')),
        ('Female',_('Female'))
    )
    
    department_id = forms.ChoiceField(label=_("Department"), choices=department_list, widget=forms.Select(attrs={"class":"form-control", "id": "department_id", "name": "department_id"}))
    service_id = forms.ChoiceField(label=_("Service"), choices=service_list, widget=forms.Select(attrs={"class":"form-control", "id": "service_id", "name": "service_id"}))
    gender = forms.ChoiceField(label=_("Gender"), choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label=_("Assignment Period"), choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    num_tel = forms.CharField(label=_("Phone Number"), widget=forms.TextInput(attrs={"class":"form-control", "placeholder": _("Enter your phone number")}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label=_("Profile Pic"), required=False, widget=forms.FileInput(attrs={"class":"form-control"}))