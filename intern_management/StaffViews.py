from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from django.utils.translation import gettext_lazy as _


from .models import CustomUser, Staffs, Department, Headquarter, Intern, SessionYearModel, Attendance, AttendanceReport, LeaveReportStaff, FeedBackStaffs, InternResult, Service
from django.utils import translation
import io
import os
from django.conf import settings


from django.template.loader import get_template
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, SimpleDocTemplate, PageBreak
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.enums import TA_LEFT, TA_CENTER
# from reportlab.lib import utils
# from reportlab.platypus import Paragraph

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

    #Fetch Attendance Data by Asignments
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

    lang_code = request.GET.get('lang', None)
    if lang_code:
        # Activate the desired language
        translation.activate(lang_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code

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

def generate_leave_staff_pdf(request):
    staff = request.user
    response = HttpResponse(content_type='application/pdf')
    file_name = f"leave_apply_by_{staff}.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)

    table_data = [[_("Leave Date"), _("Leave Message"), _("Status")]]
    
    for lev in leave_data:
        if lev.leave_status == 1:
            status = _('Approved')
        elif lev.leave_status == 2:
            status = _('Rejected')
        else:
            status = _('Pending')
        row = [
            
            
            Paragraph(str(lev.leave_date), getSampleStyleSheet()["BodyText"]),
            Paragraph(lev.leave_message, getSampleStyleSheet()["BodyText"]),  # Use BodyText style for inline formatting
            Paragraph(status, getSampleStyleSheet()["BodyText"]),
         
        ]
        table_data.append(row)

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
    title = _(f'Leave Apply by Staff {staff}')
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
    elements.append(table)
    elements.append(Spacer(0, 10))

    doc.build(elements)
    
    return response

def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, _("Invalid Method"))
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStaff(staff_id=staff_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, _("Applied for Leave."))
            return redirect('staff_apply_leave')
        except:
            messages.error(request, _("Failed to Apply Leave"))
            return redirect('staff_apply_leave')


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "staff_template/staff_feedback_template.html", context)

def generate_message_staff_pdf(request):
    staff = request.user
    response = HttpResponse(content_type='application/pdf')
    file_name = f"message_apply_by_{staff}.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)

    table_data = [[_("Message"), _("Message Reply")]]
    
    for fed in feedback_data:
        
        row = [

            Paragraph(str(fed.feedback), getSampleStyleSheet()["BodyText"]),
            Paragraph(fed.feedback_reply, getSampleStyleSheet()["BodyText"]),  # Use BodyText style for inline formatting
        ]
        table_data.append(row)

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
    title = _(f'Messages Apply by Staff {staff}')
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
    elements.append(table)
    elements.append(Spacer(0, 10))

    doc.build(elements)
    
    return response

def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, _("Invalid Method."))
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, _("Message Sent."))
            return redirect('staff_feedback')
        except:
            messages.error(request, _("Failed to Send Message."))
            return redirect('staff_feedback')


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_interns(request):
    # Getting Values from Ajax POST 'Fetch Intern'
    headquarter_id = request.POST.get("headquarter")
    session_year = request.POST.get("session_year")

    
    
    headquarter_model = Headquarter.objects.get(id=headquarter_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    interns = Intern.objects.filter(service_id=headquarter_model.service_id, session_year_id=session_model)

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

def generate_assignments_staff_pdf(request):
    staff = request.user
   
    response = HttpResponse(content_type='application/pdf')
    file_name = f"assignments_{staff}_details"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Create a SimpleDocTemplate instance
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Table data and styles
    assignments = Headquarter.objects.filter(staff_id=request.user.id)
    table_data = [[_("Assignment Name"), _("Department"), _("Service"), _("Start Period"), _("End Period")]]

    for assignment in assignments:
        # Combine last name and email in one cell with inline styles
        full_name_staff = _(f"<b>{assignment.headquarter_name}</b>")
        row = [
            
            
            Paragraph(full_name_staff, getSampleStyleSheet()["BodyText"]),
            Paragraph(assignment.department_id.department_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(assignment.service_id.service_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(str(assignment.session_year_id.session_start_year), getSampleStyleSheet()["BodyText"]),
            Paragraph(str(assignment.session_year_id.session_end_year), getSampleStyleSheet()["BodyText"]),
            
            # service.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]
        table_data.append(row)

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
    title = _("Assignments Details")
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
    elements.append(table)
   

    
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    file_name = f"assignments_{staff}_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    response.write(pdf)

    return response


def view_intern(request):
    
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    service_id_list = []
    for headquarter in headquarters:
        service = Service.objects.get(id=headquarter.service_id.id)
        service_id_list.append(service.id)
    
    final_service = []
    # Removing Duplicate Department Id
    for service_id in service_id_list:
        if service_id not in final_service:
            final_service.append(service_id)

    intern = Intern.objects.filter(service_id__in=final_service)

    context = {
        "intern": intern
    }
    return render(request, 'staff_template/view_intern_template.html', context)



def generate_employee_under_staff_pdf(request):
    staff = request.user
    response = HttpResponse(content_type='application/pdf')
    file_name = "employees_under_{staff}_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Table data and styles
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    
    service_id_list = []
    for headquarter in headquarters:
        service = Service.objects.get(id=headquarter.service_id.id)
        service_id_list.append(service.id)
        
    
    final_service = []
    # Removing Duplicate Department Id
    for service_id in service_id_list:
        if service_id not in final_service:
            final_service.append(service_id)

    interns = Intern.objects.filter(service_id__in=final_service)

    table_data = [[_("First Name"), _("Last Name"), _("Email"), _("Phone number"), _("Department"), _("Service")]]

    for intern in interns:
        # Combine last name and email in one cell with inline styles
        #name_email = f"<b>{intern.admin.last_name}</b><br/>{intern.admin.email}"
        row = [
            
            
            Paragraph(intern.admin.first_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(intern.admin.last_name, getSampleStyleSheet()["BodyText"]),  # Use BodyText style for inline formatting
            #intern.admin.last_name,
            #intern.admin.username,
            Paragraph(intern.admin.email, getSampleStyleSheet()["BodyText"]),
            Paragraph(intern.numero_telephone, getSampleStyleSheet()["BodyText"]),
            #intern.address,
            #intern.gender,
            
            #intern.profile_pic,
            Paragraph(intern.department_id.department_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(intern.service_id.service_name, getSampleStyleSheet()["BodyText"]),
            
            
            #intern.profile_pic.url if intern.profile_pic else "",
        ]
        table_data.append(row)

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
    title = _(f'Employees Under {staff}')
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
    elements.append(table)
    elements.append(Spacer(0, 10))

    doc.build(elements)
    
    return response

def intern_view_result_by_staff(request):
    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    service_id_list = []
    for headquarter in headquarters:
        service = Service.objects.get(id=headquarter.service_id.id)
        service_id_list.append(service.id)
    
    final_service = []
    # Removing Duplicate Department Id
    for service_id in service_id_list:
        if service_id not in final_service:
            final_service.append(service_id)

    interns_list = Intern.objects.filter(service_id__in=final_service)
    
    intern_result = []
    for inte in interns_list:
        intern = InternResult.objects.filter(intern_id=inte.id)
        intern_result.extend(intern)
    print(intern_result)
    context = {
        "intern_result": intern_result
    }
    return render(request, "staff_template/intern_view_result.html", context)

def generate_result_employee_under_staff_pdf(request):
    staff = request.user
    response = HttpResponse(content_type='application/pdf')
    file_name = f"result_employees_under_{staff}_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    service_id_list = []
    for headquarter in headquarters:
        service = Service.objects.get(id=headquarter.service_id.id)
        service_id_list.append(service.id)
    
    final_service = []
    # Removing Duplicate Department Id
    for service_id in service_id_list:
        if service_id not in final_service:
            final_service.append(service_id)

    interns_list = Intern.objects.filter(service_id__in=final_service)
    
    intern_result = []
    for inte in interns_list:
        intern = InternResult.objects.filter(intern_id=inte.id)
        intern_result.extend(intern)

    table_data = [[_("Assignment"), _("Assignment Mark"), _("Status")]]

    for intern in intern_result:
        if intern.headquarter_assignment_marks < 10:
            status = _("Bad Work")
        elif intern.headquarter_assignment_marks >= 10 and intern.headquarter_assignment_marks <= 13:
            status = _('Normal Work')
        elif intern.headquarter_assignment_marks > 13 and intern.headquarter_assignment_marks < 16:
            status = _("Good Work")
        elif intern.headquarter_assignment_marks >= 16 and intern.headquarter_assignment_marks <= 18:
            status = _("Amazing Work")
        else:
            status = _("wonderful Work")
        row = [
            
            
            Paragraph(intern.headquarter_id.headquarter_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(str(intern.headquarter_assignment_marks), getSampleStyleSheet()["BodyText"]),  # Use BodyText style for inline formatting
            Paragraph(status, getSampleStyleSheet()["BodyText"]),
         
        ]
        table_data.append(row)

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
    title = _(f'Employees Under {staff}')
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
    elements.append(table)
    elements.append(Spacer(0, 10))

    doc.build(elements)
    
    return response

@csrf_exempt
def get_attendance_dates(request):
    

    # Getting Values from Ajax POST 'Fetch Employé'
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
    # Getting Values from Ajax POST 'Fetch Intern'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Employee Id and Employee Name Only
    list_data = []

    for intern in attendance_data:
        data_small={"id":intern.intern_id.admin.id, "name":intern.intern_id.admin.first_name+" "+intern.intern_id.admin.last_name, "status":intern.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def generate_attendance_employee_under_staff_pdf(request):
    staff = request.user
    response = HttpResponse(content_type='application/pdf')
    file_name = f"attendance_employees_under_{staff}.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    headquarters = Headquarter.objects.filter(staff_id=request.user.id)
    service_id_list = []
    for headquarter in headquarters:
        service = Service.objects.get(id=headquarter.service_id.id)
        service_id_list.append(service.id)
    
    final_service = []
    # Removing Duplicate Department Id
    for service_id in service_id_list:
        if service_id not in final_service:
            final_service.append(service_id)

    interns = Intern.objects.filter(service_id__in=final_service)
    
    

    table_data = [[_("First Name"), _("Last Name"), _("Date"), _("Status")]]

    
    intern_totals = {}

    
    
    unique_combinations = set()
    for inte in interns:

        attendance_data = AttendanceReport.objects.filter(intern_id=inte.id)
        # Variables to store totals
        unique_dates = set()
        total_present = 0
        total_absent = 0

        for intern in attendance_data:
          
          intern_attendance_tuple = (intern.intern_id.id, str(intern.attendance_id.attendance_date))
          if intern_attendance_tuple not in unique_combinations:
            # If not, add the tuple to the set and process the data
            unique_combinations.add(intern_attendance_tuple)

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

        # Calculate total days
        total_days = len(unique_dates)

        intern_totals[inte.id] = {
            'total_days': total_days,
            'total_present': total_present,
            'total_absent': total_absent,
        }

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
    title = _(f'Employees Attendance Under Staff {staff}')
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

    
    elements.append(table)
    
    elements.append(PageBreak())

    # Create a table to display intern totals
    total_table_data = [[_("Employee Name"), _("Total Days"), _("Total Present"), _("Total Absent")]]
    for intern_id, totals in intern_totals.items():
        intern_name = Intern.objects.get(id=intern_id).admin.first_name + " " + Intern.objects.get(id=intern_id).admin.last_name
        total_row = [
            Paragraph(intern_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(str(totals['total_days']), getSampleStyleSheet()["BodyText"]),
            Paragraph(str(totals['total_present']), getSampleStyleSheet()["BodyText"]),
            Paragraph(str(totals['total_absent']), getSampleStyleSheet()["BodyText"]),
        ]
        total_table_data.append(total_row)
    
    num_columns = len(total_table_data[0])
    page_width, page_height = letter
    column_width = page_width / num_columns


    title = _('Total Employees Attendance')
    title_style = getSampleStyleSheet()["Title"]
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)
    elements.append(Spacer(1, 12))  # Add some space between title and table

    total_table = Table(total_table_data, colWidths=[column_width] * num_columns, repeatRows=1)
    total_table.setStyle(TableStyle([
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

    elements.append(Spacer(1, 12))  # Add some space between tables
    elements.append(total_table)

    doc.build(elements)
    
    return response


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
        messages.error(request, _("Invalid Method!"))
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

            messages.success(request, _("Profile Updated Successfully"))
            return redirect('staff_profile')
        except:
            messages.error(request, _("Failed to Update Profile"))
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
        messages.error(request, _("Invalid Method"))
        return redirect('staff_add_result')
    else:
        intern_admin_id = request.POST.get('intern_list')
        assignment_marks = request.POST.get('assignment_marks')
        # exam_marks = request.POST.get('exam_marks')
        headquarter_id = request.POST.get('headquarter')

        intern_obj = Intern.objects.get(admin=intern_admin_id)
        headquarter_obj = Headquarter.objects.get(id=headquarter_id)

        try:
            # Check if Students Result Already Exists or not
            check_exist = InternResult.objects.filter(headquarter_id=headquarter_obj, intern_id=intern_obj).exists()
            if check_exist:
                result = InternResult.objects.get(headquarter_id=headquarter_obj, intern_id=intern_obj)
                result.headquarter_assignment_marks = assignment_marks
                # result.headquarter_exam_marks = exam_marks
                result.save()
                messages.success(request, _("Result Updated Successfully!"))
                return redirect('staff_add_result')
            else:
                result = InternResult(intern_id=intern_obj, headquarter_id=headquarter_obj, headquarter_assignment_marks=assignment_marks) # headquarter_exam_marks=exam_marks, 
                result.save()
                messages.success(request, _("Result Added Successfully!"))
                return redirect('staff_add_result')
        except:
            messages.error(request, _("Failed to Add Result!"))
            return redirect('staff_add_result')