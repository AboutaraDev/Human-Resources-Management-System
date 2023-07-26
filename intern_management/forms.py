from django import forms 
from .models import Department, SessionYearModel

from django.utils.translation import gettext_lazy as _



class DateInput(forms.DateInput):
    input_type = "date"


class AddInternForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label=_("Password"), max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label=_("First Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label=_("Last Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label=_("Username"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label=_("Address"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    #For Displaying Departments
    try:
        departments = Department.objects.all()
        department_list = []
        for department in departments:
            single_department = (department.id, department.department_name)
            department_list.append(single_department)
        
        
    except:
        department_list = []
    
    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []
    
    gender_list = (
        ('Male',_('Male')),
        ('Female',_('Female'))
    )
    
    department_id = forms.ChoiceField(label=_("Department"), choices=department_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label=_("Gender"), choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label=_("Session Year"), choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label=_("Profile Pic"), required=False, widget=forms.FileInput(attrs={"class":"form-control"}))



class EditInternForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label=_("First Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label=_("Last Name"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label=_("Username"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label=_("Address"), max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    #For Displaying Departments
    try:
        departments = Department.objects.all()
        department_list = []
        for department in departments:
            single_department = (department.id, department.department_name)
            department_list.append(single_department)
    except:
        department_list = []

    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []

    
    gender_list = (
        ('Male',_('Male')),
        ('Female',_('Female'))
    )
    
    department_id = forms.ChoiceField(label=_("Department"), choices=department_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label=_("Gender"), choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label=_("Session Year"), choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label=_("Profile Pic"), required=False, widget=forms.FileInput(attrs={"class":"form-control"}))