from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json


from .models import CustomUser, Staffs, Department, Headquarter, Intern, SessionYearModel, Attendance, AttendanceReport, LeaveReportStaff, FeedBackStaffs, InternResult


def staff_home(request):
    # Fetching All Interns under Staff

    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    department_id_list = []
    for headquarter in headquarters:
        department = Department.objects.get(id=headquarter.department_id.id)
        department_id_list.append(department.id)
    
    final_department = []
    # Removing Duplicate Department Id
    for department_id in department_id_list:
        if department_id not in final_department:
            final_department.append(department_id)
    
    interns_count = Intern.objects.filter(department_id__in=final_department).count()
    headquarter_count = headquarters.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(headquarter_id__in=headquarters).count()
    # Fetch All Approve Leave
    staff = Staffs.objects.get(admin=request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()

    #Fetch Attendance Data by Subjects
    headquarter_list = []
    attendance_list = []
    for headquarter in headquarters:
        attendance_count1 = Attendance.objects.filter(headquarter_id=headquarter.id).count()
        headquarter_list.append(headquarter.headquarter_name)
        attendance_list.append(attendance_count1)

    interns_attendance = Intern.objects.filter(department_id__in=final_department)
    intern_list = []
    intern_list_attendance_present = []
    intern_list_attendance_absent = []
    for intern in interns_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, intern_id=intern.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, intern_id=intern.id).count()
        intern_list.append(intern.admin.first_name+" "+ intern.admin.last_name)
        intern_list_attendance_present.append(attendance_present_count)
        intern_list_attendance_absent.append(attendance_absent_count)

    context={
        "interns_count": interns_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "headquarter_count": headquarter_count,
        "headquarter_list": headquarter_list,
        "attendance_list": attendance_list,
        "intern_list": intern_list,
        "attendance_present_list": intern_list_attendance_present,
        "attendance_absent_list": intern_list_attendance_absent
    }
    return render(request, "staff_template/staff_home_template.html", context)



def staff_take_attendance(request):
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "headquarters": headquarters,
        "session_years": session_years
    }
    return render(request, "staff_template/take_attendance_template.html", context)


def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStaff(staff_id=staff_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('staff_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('staff_apply_leave')


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "staff_template/staff_feedback_template.html", context)


def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('staff_feedback')


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_interns(request):
    # Getting Values from Ajax POST 'Fetch Intern'
    headquarter_id = request.POST.get("headquarter")
    session_year = request.POST.get("session_year")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    headquarter_model = Headquarter.objects.get(id=headquarter_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    interns = Intern.objects.filter(department_id=headquarter_model.department_id, session_year_id=session_model)

    # Only Passing Intern Id and Student Name Only
    list_data = []

    for intern in interns:
        data_small={"id":intern.admin.id, "name":intern.admin.first_name+" "+intern.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staf Take Attendance form via AJAX (JavaScript)
    # Use getlist to access HTML Array/List Input Data
    intern_ids = request.POST.get("intern_ids")
    headquarter_id = request.POST.get("headquarter_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    headquarter_model = Headquarter.objects.get(id=headquarter_id)
    session_year_model = SessionYearModel.objects.get(id=session_year_id)

    json_intern = json.loads(intern_ids)
    # print(dict_student[0]['id'])

    # print(student_ids)
    try:
        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(headquarter_id=headquarter_model, attendance_date=attendance_date, session_year_id=session_year_model)
        attendance.save()

        for stud in json_intern:
            # Attendance of Individual Student saved on AttendanceReport Model
            intern = Intern.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(intern_id=intern, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")




def staff_update_attendance(request):
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "headquarters": headquarters,
        "session_years": session_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)

def view_headquarter(request):
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    context = {
        "headquarters": headquarters
    }
    return render(request, 'staff_template/manage_headquarter_template.html', context)

def view_intern(request):
    
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    department_id_list = []
    for headquarter in headquarters:
        department = Department.objects.get(id=headquarter.department_id.id)
        department_id_list.append(department.id)
    
    final_department = []
    # Removing Duplicate Department Id
    for department_id in department_id_list:
        if department_id not in final_department:
            final_department.append(department_id)

    intern = Intern.objects.filter(department_id__in=final_department)

    context = {
        "intern": intern
    }
    return render(request, 'staff_template/view_intern_template.html', context)

def intern_view_result_by_staff(request):
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    department_id_list = []
    for headquarter in headquarters:
        department = Department.objects.get(id=headquarter.department_id.id)
        department_id_list.append(department.id)
    
    final_department = []
    # Removing Duplicate Department Id
    for department_id in department_id_list:
        if department_id not in final_department:
            final_department.append(department_id)

    interns_list = Intern.objects.filter(department_id__in=final_department)
    
    intern_result = []
    for inte in interns_list:
        intern = InternResult.objects.filter(intern_id=inte.id)
        intern_result.extend(intern)
    print(intern_result)
    context = {
        "intern_result": intern_result
    }
    return render(request, "staff_template/intern_view_result.html", context)

@csrf_exempt
def get_attendance_dates(request):
    

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
def get_attendance_intern(request):
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


@csrf_exempt
def update_attendance_data(request):
    intern_ids = request.POST.get("intern_ids")

    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_intern = json.loads(intern_ids)

    try:
        
        for inte in json_intern:
            # Attendance of Individual Student saved on AttendanceReport Model
            intern = Intern.objects.get(admin=inte['id'])

            attendance_report = AttendanceReport.objects.get(intern_id=intern, attendance_id=attendance)
            attendance_report.status=inte['status']

            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context={
        "user": user,
        "staff": staff
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')



def staff_add_result(request):
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "headquarters": headquarters,
        "session_years": session_years,
    }
    return render(request, "staff_template/add_result_template.html", context)




def staff_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_result')
    else:
        intern_admin_id = request.POST.get('intern_list')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')
        headquarter_id = request.POST.get('headquarter')

        intern_obj = Intern.objects.get(admin=intern_admin_id)
        headquarter_obj = Headquarter.objects.get(id=headquarter_id)

        try:
            # Check if Students Result Already Exists or not
            check_exist = InternResult.objects.filter(headquarter_id=headquarter_obj, intern_id=intern_obj).exists()
            if check_exist:
                result = InternResult.objects.get(headquarter_id=headquarter_obj, intern_id=intern_obj)
                result.headquarter_assignment_marks = assignment_marks
                result.headquarter_exam_marks = exam_marks
                result.save()
                messages.success(request, "Result Updated Successfully!")
                return redirect('staff_add_result')
            else:
                result = InternResult(intern_id=intern_obj, headquarter_id=headquarter_obj, headquarter_exam_marks=exam_marks, headquarter_assignment_marks=assignment_marks)
                result.save()
                messages.success(request, "Result Added Successfully!")
                return redirect('staff_add_result')
        except:
            messages.error(request, "Failed to Add Result!")
            return redirect('staff_add_result')