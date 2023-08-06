from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
import datetime # To Parse input DateTime into Python Date Time Object

from .models import CustomUser, Department, Headquarter, Intern, Attendance, AttendanceReport, LeaveReportIntern, FeedBackIntern, InternResult
from django.utils.translation import gettext_lazy as _
from django.utils import translation
import io
import os
from django.conf import settings


from django.template.loader import get_template
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import utils
from reportlab.platypus import Paragraph


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

    lang_code = request.GET.get('lang', None)
    if lang_code:
        # Activate the desired language
        translation.activate(lang_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    
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

def generate_attendance_employee_pdf(request):
    emp = request.user
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=attendance_employee_{emp}.pdf'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Table data and styles
    #attendance_date = request.POST.get('attendance_date')
    try:
     intern_instance = Intern.objects.get(admin=emp)
     attendance_data = AttendanceReport.objects.filter(intern_id=intern_instance)
    except Intern.DoesNotExist:
        # Handle the case where the employee is not associated with an intern
        attendance_data = []

    table_data = [[_("First Name"), _("Last Name"), _("Date"), _("Status")]]

    # Variables to store totals
    unique_dates = set()
    total_present = 0
    total_absent = 0

    for intern in attendance_data:
        

        if intern.status == True:
            total_present += 1
            name = _('Present')
        elif intern.status == False:
            total_absent += 1
            name = _('Absent')
        else:
            name = _('None')

        row = [
            
            
            Paragraph(intern.intern_id.admin.first_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(intern.intern_id.admin.last_name, getSampleStyleSheet()["BodyText"]),  # Use BodyText style for inline formatting  
            Paragraph(str(intern.attendance_id.attendance_date), getSampleStyleSheet()["BodyText"]),    
            Paragraph(name, getSampleStyleSheet()["BodyText"]),

            
        ]
        table_data.append(row)
        # Calculate unique attendance dates
        unique_dates.add(str(intern.attendance_id.attendance_date))

     # Calculate the column widths based on the page size and number of columns
    num_columns = len(table_data[0])
    page_width, page_height = letter
    column_width = page_width / num_columns

    elements = []

     # Get the full paths of the logo images
    logo1_path = os.path.join(settings.MEDIA_ROOT, 'provinceZagoraLogoo.png')
    logo2_path = os.path.join(settings.MEDIA_ROOT, 'provinceZagoraLogoo.png')

    # Check if the logo image files exist
    if os.path.exists(logo1_path) and os.path.exists(logo2_path):
        # Add the logos to the PDF
        logo1 = Image(logo1_path)
        logo2 = Image(logo2_path)

        # Set the sizes of the logos
        logo1.drawHeight = 150
        logo1.drawWidth = 150

        logo2.drawHeight = 50
        logo2.drawWidth = 150

        # Position the logos on the top corners
        logo1_pos_x, logo1_pos_y = 40, 750  # Top left corner
        logo2_pos_x, logo2_pos_y = page_width - 40 - logo2.drawWidth, 750  # Top right corner

        # Add the logos directly to the elements list
        elements.extend([
            logo1,
            #logo2,
        ])

        
    
    # Add title to the PDF
    title = _(f'Employee {emp} Attendance')
    title_style = getSampleStyleSheet()["Title"]
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)
    elements.append(Spacer(1, 12))  # Add some space between title and table
    
    table = Table(table_data, colWidths=[column_width] * num_columns, repeatRows=1)
    table.setStyle(TableStyle([
            # ... Table styles ...
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment of text within cells
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Text color
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
            ('TOPPADDING', (0, 0), (-1, -1), 10),  # Top padding for cells
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),  # Bottom padding for cells
            ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Left padding for cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Right padding for cells
    ]))

    # Calculate total days
    total_days = len(unique_dates)

    elements.append(table)
    elements.append(Paragraph(_("Total Days: ") + str(total_days), getSampleStyleSheet()["BodyText"]))
    elements.append(Paragraph(_(f"Total {intern.intern_id.admin.first_name} Present: ") + str(total_present), getSampleStyleSheet()["BodyText"]))
    elements.append(Paragraph(_(f"Total {intern.intern_id.admin.first_name} Absent: ") + str(total_absent), getSampleStyleSheet()["BodyText"]))
    elements.append(Spacer(0, 10))

    doc.build(elements)
    
    return response


def intern_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, _("Invalid Method"))
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
        messages.error(request, _("Invalid Method"))
        return redirect('intern_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        intern_obj = Intern.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportIntern(intern_id=intern_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, _("Applied for Leave."))
            return redirect('intern_apply_leave')
        except:
            messages.error(request, _("Failed to Apply Leave"))
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
        messages.error(request, _("Invalid Method."))
        return redirect('intern_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        intern_obj = Intern.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackIntern(intern_id=intern_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, _("Feedback Sent."))
            return redirect('intern_feedback')
        except:
            messages.error(request, _("Failed to Send Feedback."))
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
        messages.error(request, _("Invalid Method!"))
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
            
            messages.success(request, _("Profile Updated Successfully"))
            return redirect('intern_profile')
        except:
            messages.error(request, _("Failed to Update Profile"))
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



