from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import json

from .models import CustomUser, Staffs, Department, Headquarter, Intern, SessionYearModel,  LeaveReportIntern, LeaveReportStaff, Attendance, AttendanceReport, FeedBackIntern, LeaveReportIntern, LeaveReportStaff, FeedBackIntern, FeedBackStaffs, NotificationIntern, NotificationStaffs, InternResult
                                     
from .forms import AddInternForm, EditInternForm

from django.views.generic import TemplateView

from django.shortcuts import redirect
from django.utils.translation import activate
from django.conf import settings

    
def admin_home(request):
    all_intern_count = Intern.objects.all().count()
    headquarter_count = Headquarter.objects.all().count()
    department_count = Department.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    department_all = Department.objects.all()
    department_name_list = []
    headquarter_count_list = []
    intern_count_list_in_department = []

    for department in department_all:
        headquarters = Headquarter.objects.filter(department_id=department.id).count()
        interns = Intern.objects.filter(department_id=department.id).count()
        department_name_list.append(department.department_name)
        headquarter_count_list.append(headquarters)
        intern_count_list_in_department.append(interns)
    
    headquarter_all = Headquarter.objects.all()
    headquarter_list = []
    intern_count_list_in_headquarter = []
    for headquarter in headquarter_all:
        department = Department.objects.get(id=headquarter.department_id.id)
        intern_count = Intern.objects.filter(department_id=department.id).count()
        headquarter_list.append(headquarter.headquarter_name)
        intern_count_list_in_headquarter.append(intern_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        headquarter_ids = Headquarter.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(headquarter_id__in=headquarter_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Interns 
    intern_attendance_present_list=[]
    intern_attendance_leave_list=[]
    intern_name_list=[]

    interns = Intern.objects.all()
    for intern in interns:
        attendance = AttendanceReport.objects.filter(intern_id=intern.id, status=True).count()
        absent = AttendanceReport.objects.filter(intern_id=intern.id, status=False).count()
        leaves = LeaveReportIntern.objects.filter(intern_id=intern.id, leave_status=1).count()
        intern_attendance_present_list.append(attendance)
        intern_attendance_leave_list.append(leaves+absent)
        intern_name_list.append(intern.admin.first_name)


    context={
        "all_intern_count": all_intern_count,
        "headquarter_count": headquarter_count,
        "department_count": department_count,
        "staff_count": staff_count,
        "department_name_list": department_name_list,
        "headquarter_count_list": headquarter_count_list,
        "intern_count_list_in_department": intern_count_list_in_department,
        "headquarter_list": headquarter_list,
        "intern_count_list_in_headquarter": intern_count_list_in_headquarter,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "intern_attendance_present_list": intern_attendance_present_list,
        "intern_attendance_leave_list": intern_attendance_leave_list,
        "intern_name_list": intern_name_list,
    }
   
    return render(request, "hod_template/home_content.html", context)


def my_view_lang(request):
    # Get the selected language code from the query parameters
    language_code = request.GET.get('language')

    # Activate the selected language for this request
    if language_code:
        activate(language_code)

    # Your view logic here
    # ...

    return render(request, 'my_template.html')

def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=CustomUser.STAFF)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')
        

        
def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)

def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')


def add_department(request):
    return render(request, "hod_template/add_department_template.html")


def add_department_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_department')
    else:
        department = request.POST.get('department')
        try:
            department_model = Department(department_name=department)
            department_model.save()
            messages.success(request, "Department Added Successfully!")
            return redirect('add_department')
        except:
            messages.error(request, "Failed to Add Department!")
            return redirect('add_department')

def manage_department(request):
    departments = Department.objects.all()
    context = {
        "departments": departments
    }
    return render(request, 'hod_template/manage_department_template.html', context)

def edit_department(request, department_id):
    department = Department.objects.get(id=department_id)
    context = {
        "department": department,
        "id": department_id
    }
    return render(request, 'hod_template/edit_department_template.html', context)


def edit_department_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        department_id = request.POST.get('department_id')
        department_name = request.POST.get('department')

        try:
            department = Department.objects.get(id=department_id)
            department.department_name = department_name
            department.save()

            messages.success(request, "Department Updated Successfully.")
            return redirect('/edit_department/'+department_id)

        except:
            messages.error(request, "Failed to Update Department.")
            return redirect('/edit_department/'+department_id)


def delete_department(request, department_id):
    department = Department.objects.get(id=department_id)
    try:
        department.delete()
        messages.success(request, "Department Deleted Successfully.")
        return redirect('manage_department')
    except:
        messages.error(request, "Failed to Delete Department.")
        return redirect('manage_department')


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)

def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_intern(request):
    form = AddInternForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_intern_template.html', context)




def add_intern_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_intern')
    else:
        form = AddInternForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            department_id = form.cleaned_data['department_id']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None


            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type= CustomUser.INTERN)
                user.intern.address = address

                department_obj = Department.objects.get(id=department_id)
                user.intern.department_id = department_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.intern.session_year_id = session_year_obj

                user.intern.gender = gender
                user.intern.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Intern Added Successfully!")
                return redirect('add_intern')
            except:
                messages.error(request, "Failed to Add Intern!!:")
                return redirect('add_intern')
        else:
            return redirect('add_intern')



def manage_intern(request):
    intern = Intern.objects.all()
    context = {
        "intern": intern
    }
    return render(request, 'hod_template/manage_intern_template.html', context)

def edit_intern(request, intern_id):
    # Adding Student ID into Session Variable
    request.session['intern_id'] = intern_id

    intern = Intern.objects.get(admin=intern_id)
    form = EditInternForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = intern.admin.email
    form.fields['username'].initial = intern.admin.username
    form.fields['first_name'].initial = intern.admin.first_name
    form.fields['last_name'].initial = intern.admin.last_name
    form.fields['address'].initial = intern.address
    form.fields['department_id'].initial = intern.department_id.id
    form.fields['gender'].initial = intern.gender
    form.fields['session_year_id'].initial = intern.session_year_id.id

    context = {
        "id": intern_id,
        "username": intern.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_intern_template.html", context)


def edit_intern_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        intern_id = request.session.get('intern_id')
        if intern_id == None:
            return redirect('/manage_intern')

        form = EditInternForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            department_id = form.cleaned_data['department_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=intern_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                intern_model = Intern.objects.get(admin=intern_id)
                intern_model.address = address

                department = Department.objects.get(id=department_id)
                intern_model.department_id = department

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                intern_model.session_year_id = session_year_obj

                intern_model.gender = gender
                if profile_pic_url != None:
                    intern_model.profile_pic = profile_pic_url
                intern_model.save()
                # Delete intern_id SESSION after the data is updated
                del request.session['intern_id']

                messages.success(request, "Intern Updated Successfully!")
                return redirect('/edit_intern/'+intern_id)
            except:
                messages.success(request, "Failed to Update Intern.")
                return redirect('/edit_intern/'+intern_id)
        else:
            return redirect('/edit_intern/'+intern_id)


def delete_intern(request, intern_id):
    intern = Intern.objects.get(admin=intern_id)
    try:
        intern.delete()
        messages.success(request, "Intern Deleted Successfully.")
        return redirect('manage_intern')
    except:
        messages.error(request, "Failed to Delete Intern.")
        return redirect('manage_intern')

def add_headquarter(request):
    departments = Department.objects.all()
    staffs = CustomUser.objects.filter(user_type= CustomUser.STAFF)
    context = {
        "departments": departments,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_headquarter_template.html', context)



def add_headquarter_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_headquarter')
    else:
        headquarter_name = request.POST.get('headquarter')
        print(headquarter_name)
        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id)
        
        print(department)

        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)
        
        print(staff)
        try:
            
            headquarterN = Headquarter(headquarter_name=headquarter_name, department_id=department, staff_id=staff)
            headquarterN.save()
            messages.success(request, "Headquarter Added Successfully!")
            return redirect('add_headquarter')
        except Exception as e:
            print("Error:", e)
            messages.error(request, "Failed to Add Headquarter!")
            return redirect('add_headquarter')



def manage_headquarter(request):
    headquarters = Headquarter.objects.all()
    context = {
        "headquarters": headquarters
    }
    return render(request, 'hod_template/manage_headquarter_template.html', context)


def edit_headquarter(request, headquarter_id):
    headquarter = Headquarter.objects.get(id=headquarter_id)
    departments = Department.objects.all()
    staffs = CustomUser.objects.filter(user_type=CustomUser.STAFF)
    context = {
        "headquarter": headquarter,
        "departments": departments,
        "staffs": staffs,
        "id": headquarter_id
    }
    return render(request, 'hod_template/edit_headquarter_template.html', context)


def edit_headquarter_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        headquarter_id = request.POST.get('headquarter_id')
        headquarter_name = request.POST.get('headquarter')
        department_id = request.POST.get('department')
        staff_id = request.POST.get('staff')

        try:
            headquarter = Headquarter.objects.get(id=headquarter_id)
            headquarter.headquarter_name = headquarter_name

            department = Department.objects.get(id=department_id)
            headquarter.department_id = department

            staff = CustomUser.objects.get(id=staff_id)
            headquarter.staff_id = staff
            
            headquarter.save()

            messages.success(request, "Headquarter Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_headquarter", kwargs={"headquarter_id":headquarter_id}))

        except:
            messages.error(request, "Failed to Update Headquarter.")
            return HttpResponseRedirect(reverse("edit_headquarter", kwargs={"headquarter_id":headquarter_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_headquarter(request, headquarter_id):
    headquarter = Headquarter.objects.get(id=headquarter_id)
    try:
        headquarter.delete()
        messages.success(request, "Headquarter Deleted Successfully.")
        return redirect('manage_headquarter')
    except:
        messages.error(request, "Failed to Delete Headquarter.")
        return redirect('manage_headquarter')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def intern_feedback_message(request):
    feedbacks = FeedBackIntern.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/intern_feedback_template.html', context)


@csrf_exempt
def intern_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackIntern.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def intern_leave_view(request):
    leaves = LeaveReportIntern.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/intern_leave_view.html', context)

def intern_leave_approve(request, leave_id):
    leave = LeaveReportIntern.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('intern_leave_view')


def intern_leave_reject(request, leave_id):
    leave = LeaveReportIntern.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('intern_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    headquarters = Headquarter.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "headquarters": headquarters,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    headquarter_id = request.POST.get("headquarter")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    headquarter_model = Headquarter.objects.get(id=headquarter_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(headquarter_id=headquarter_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_intern(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for intern in attendance_data:
        data_small={"id":intern.intern_id.admin.id, "name":intern.intern_id.admin.first_name+" "+intern.intern_id.admin.last_name, "status":intern.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')


def staff_profile(request):
    pass


def student_profile(requtest):
    pass

