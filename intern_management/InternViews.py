from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
import datetime # To Parse input DateTime into Python Date Time Object

from .models import CustomUser, Department, Headquarter, Intern, Attendance, AttendanceReport, LeaveReportIntern, FeedBackIntern, InternResult


def intern_home(request):
    intern_obj = Intern.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(intern_id=intern_obj).count()
    attendance_present = AttendanceReport.objects.filter(intern_id=intern_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(intern_id=intern_obj, status=False).count()

    department_obj = Department.objects.get(id=intern_obj.department_id.id)
    total_headquarters = Headquarter.objects.filter(department_id=department_obj).count()

    headquarter_name = []
    data_present = []
    data_absent = []
    headquarter_data = Headquarter.objects.filter(department_id=intern_obj.department_id)
    for headquarter in headquarter_data:
        attendance = Attendance.objects.filter(headquarter_id=headquarter.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, intern_id=intern_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, intern_id=intern_obj.id).count()
        headquarter_name.append(headquarter.headquarter_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    
    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "total_headquarters": total_headquarters,
        "headquarter_name": headquarter_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "intern_template/intern_home_template.html", context)


def intern_view_attendance(request):
    intern = Intern.objects.get(admin=request.user.id) # Getting Logged in Student Data
    department = intern.department_id # Getting Course Enrolled of LoggedIn Student
    # course = Courses.objects.get(id=student.course_id.id) # Getting Course Enrolled of LoggedIn Student
    headquarters = Headquarter.objects.filter(department_id=department) # Getting the Subjects of Course Enrolled
    context = {
        "headquarters": headquarters
    }
    return render(request, "intern_template/intern_view_attendance.html", context)


def intern_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('intern_view_attendance')
    else:
        # Getting all the Input Data
        headquarter_id = request.POST.get('headquarter')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        headquarter_obj = Headquarter.objects.get(id=headquarter_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Student Data Based on Logged in Data
        inte_obj = Intern.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), headquarter_id=headquarter_obj)
        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, intern_id=inte_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "headquarter_obj": headquarter_obj,
            "attendance_reports": attendance_reports
        }

        return render(request, 'intern_template/intern_attendance_data.html', context)
       

def intern_apply_leave(request):
    intern_obj = Intern.objects.get(admin=request.user.id)
    leave_data = LeaveReportIntern.objects.filter(intern_id=intern_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'intern_template/intern_apply_leave.html', context)


def intern_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('intern_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        intern_obj = Intern.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportIntern(intern_id=intern_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('intern_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('intern_apply_leave')


def intern_feedback(request):
    intern_obj = Intern.objects.get(admin=request.user.id)
    feedback_data = FeedBackIntern.objects.filter(intern_id=intern_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'intern_template/intern_feedback.html', context)


def intern_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('intern_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        intern_obj = Intern.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackIntern(intern_id=intern_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('intern_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('intern_feedback')


def intern_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    intern = Intern.objects.get(admin=user)

    context={
        "user": user,
        "intern": intern
    }
    return render(request, 'intern_template/intern_profile.html', context)


def intern_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('intern_profile')
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

            intern = Intern.objects.get(admin=customuser.id)
            intern.address = address
            intern.save()
            
            messages.success(request, "Profile Updated Successfully")
            return redirect('intern_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('intern_profile')


def intern_view_result(request):
    intern = Intern.objects.get(admin=request.user.id)
    intern_result = InternResult.objects.filter(intern_id=intern.id)
    context = {
        "intern_result": intern_result,
    }
    return render(request, "intern_template/intern_view_result.html", context)

def intern_view_headquarters(request):
    
    intern_obj = Intern.objects.get(admin=request.user.id)
    
    department_obj = Department.objects.get(id=intern_obj.department_id.id)
    headquarters = Headquarter.objects.filter(department_id=department_obj)
    context = {
        "headquarters": headquarters
    }
    return render(request, 'intern_template/intern_view_headquarters.html', context)



