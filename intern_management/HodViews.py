from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

import json

from .models import CustomUser, Staffs, Department, Headquarter, Intern, SessionYearModel,  LeaveReportIntern, LeaveReportStaff, Attendance, AttendanceReport, FeedBackIntern, LeaveReportIntern, LeaveReportStaff, FeedBackIntern, FeedBackStaffs, Service

                                     
from .forms import AddInternForm, EditInternForm

from django.views.generic import TemplateView

from django.shortcuts import redirect
from django.utils import translation

from django.conf import settings
import os
import io


from django.template.loader import get_template
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, SimpleDocTemplate, PageBreak
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.enums import TA_LEFT, TA_CENTER
# from reportlab.lib import utils
# from reportlab.platypus import Paragraph
    
def admin_home(request):
    all_intern_count = Intern.objects.all().count()
    headquarter_count = Headquarter.objects.all().count()
    department_count = Department.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Assignments and Interns in Each Course
    department_all = Department.objects.all()
    department_name_list = []
    headquarter_count_list = []
    intern_count_list_in_department = []

    for department in department_all:
        headquarters = Headquarter.objects.filter(department_id=department.id).count()
        interns = Intern.objects.filter(department_id=department.id).count()
        depName = _(department.department_name)
        department_name_list.append(depName)
        headquarter_count_list.append(headquarters)
        intern_count_list_in_department.append(interns)
    
    # Total Services and Each Service in Department
    total_services_count = Service.objects.all().count()
    department_services_count_list = {}

    for department in department_all:
        services_count = department.services.all().count()
        department_services_count_list[department.department_name] =  services_count

    headquarter_all = Headquarter.objects.all()
    headquarter_list = []
    intern_count_list_in_headquarter = []
    for headquarter in headquarter_all:
        department = Department.objects.get(id=headquarter.department_id.id)
        intern_count = Intern.objects.filter(department_id=department.id).count()
        hedName = _(headquarter.headquarter_name)
        headquarter_list.append(hedName)
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

    lang_code = request.GET.get('lang', None)
    if lang_code:
        # Activate the desired language
        translation.activate(lang_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
 
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
        "total_services_count" : total_services_count,
        "department_services_count_list" : department_services_count_list,
    }
   
    return render(request, "hod_template/home_content.html", context)



def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, _("Invalid Method"))
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
            messages.success(request, _("Staff Added Successfully!"))
            return redirect('add_staff')
        except:
            messages.error(request, _("Failed to Add Staff!"))
            return redirect('add_staff')
        

        
def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def generate_staff_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    file_name = "staff_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Table data and styles
    staffs = Staffs.objects.all()
    table_data = [[_("Username"), _("Email"), _("Address")]]

    for staff in staffs:
        row = [
            
            Paragraph(staff.admin.username, getSampleStyleSheet()["BodyText"]),
            Paragraph(staff.admin.email, getSampleStyleSheet()["BodyText"]),
            Paragraph(staff.address, getSampleStyleSheet()["BodyText"]),  
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
    title = _("Staffs Details")
    title_style = getSampleStyleSheet()["Title"]
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)
    elements.append(Spacer(1, 12))  # Add some space between title and table
    # Create the table
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

    # Add the table to the PDF document
    elements.append(table)
    elements.append(Spacer(0, 10))
    doc.build(elements)


    return response


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse(_("<h2>Method Not Allowed</h2>"))
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

            messages.success(request, _("Staff Updated Successfully."))
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, _("Failed to Update Staff."))
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, _("Staff Deleted Successfully."))
        return redirect('manage_staff')
    except:
        messages.error(request, _("Failed to Delete Staff."))
        return redirect('manage_staff')

def generate_department_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    file_name = "departments_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Table data and styles
    departments = Department.objects.all()
    table_data = [[_("Department Name")]]

    for department in departments:
        row = [
            
            
            Paragraph(department.department_name, getSampleStyleSheet()["BodyText"]),
            
            
            
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
    title = _("Departments Details")
    title_style = getSampleStyleSheet()["Title"]
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)
    elements.append(Spacer(1, 12))  # Add some space between title and table
    # Create the table
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

    # Add the table to the PDF document
    elements.append(table)
    elements.append(Spacer(0, 10))
    doc.build(elements)


    return response

def add_department(request):
    return render(request, "hod_template/add_department_template.html")


def add_department_save(request):
    if request.method != "POST":
        messages.error(request, _("Invalid Method!"))
        return redirect('add_department')
    else:
        department = request.POST.get('department')
        try:
            department_model = Department(department_name=department)
            department_model.save()
            messages.success(request, _("Department Added Successfully!"))
            return redirect('add_department')
        except:
            messages.error(request, _("Failed to Add Department!"))
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
        HttpResponse(_("Invalid Method"))
    else:
        department_id = request.POST.get('department_id')
        department_name = request.POST.get('department')

        try:
            department = Department.objects.get(id=department_id)
            department.department_name = department_name
            department.save()

            messages.success(request, _("Department Updated Successfully."))
            return redirect('/edit_department/'+department_id)

        except:
            messages.error(request, _("Failed to Update Department."))
            return redirect('/edit_department/'+department_id)


def delete_department(request, department_id):
    department = Department.objects.get(id=department_id)
    try:
        department.delete()
        messages.success(request, _("Department Deleted Successfully."))
        return redirect('manage_department')
    except:
        messages.error(request, _("Failed to Delete Department."))
        return redirect('manage_department')

def generate_service_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    file_name = "services_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Table data and styles
    services = Service.objects.all()
    table_data = [[_("Service Name"), _("Department Name")]]

    for service in services:
        row = [
            Paragraph(service.service_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(service.department.department_name, getSampleStyleSheet()["BodyText"]),
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
    title = _("Services Details")
    title_style = getSampleStyleSheet()["Title"]
    title_paragraph = Paragraph(title, title_style)
    elements.append(title_paragraph)
    elements.append(Spacer(1, 12))  # Add some space between title and table
    # Create the table
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

    # Add the table to the PDF document
    elements.append(table)
    elements.append(Spacer(0, 10))
    doc.build(elements)


    return response

def add_service(request):
    departments = Department.objects.all()
    context = {
        "departments": departments
    }
    return render(request, "hod_template/add_service_template.html", context)

def add_service_save(request):
    if request.method != "POST":
        messages.error(request, _('Invalid Method'))
        return redirect('add_service')
    else:
        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id)
        try:
           service_name = request.POST.get('service')
           service_model = Service(service_name=service_name, department=department)
           service_model.save()
           messages.success(request, _("Service Added Successfully!"))
           return redirect('add_service')
        except:
           messages.error(request, _("Failed to Add Service!"))
           return redirect('add_service')


def manage_service(request):
    services = Service.objects.all()
    context = {
        "services": services
    }
    return render(request, "hod_template/manage_service_template.html", context)

def edit_service(request, service_id):
    service = Service.objects.get(id=service_id)
    departments = Department.objects.all()
    
    context = {
        "service": service,
        "departments": departments,
        "id": service_id
    }
    return render(request, 'hod_template/edit_service_template.html', context)


def edit_service_save(request):
    if request.method != "POST":
        HttpResponse(_("Invalid Method."))
    else:
        service_id = request.POST.get('service_id')
        service_name = request.POST.get('service')
        department_id = request.POST.get('department')
        

        try:
            service = Service.objects.get(id=service_id)
            service.service_name = service_name

            department = Department.objects.get(id=department_id)
            service.department = department
            
            service.save()

            messages.success(request, _("Service Updated Successfully."))
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_service", kwargs={"service_id":service_id}))

        except:
            messages.error(request, _("Failed to Update Service."))
            return HttpResponseRedirect(reverse("edit_service", kwargs={"service_id":service_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_service(request, service_id):
    service = Service.objects.get(id=service_id)
    try:
        service.delete()
        messages.success(request, _("Service Deleted Successfully."))
        return redirect('manage_service')
    except:
        messages.error(request, _("Failed to Delete Service."))
        return redirect('manage_service')



def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, _("'Invalid Method"))
        return redirect('add_department')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, _("Assignment Period added Successfully!"))
            return redirect("add_session")
        except:
            messages.error(request, _("Failed to Add Assignment Period"))
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
        messages.error(request, _("Invalid Method!"))
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

            messages.success(request, _("Assignment Period Updated Successfully."))
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, _("Failed to Update Assignment Period."))
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, _("Assignment Period Deleted Successfully."))
        return redirect('manage_session')
    except:
        messages.error(request, _("Failed to Delete Assignment Period."))
        return redirect('manage_session')

def generate_intern_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    file_name = "employees_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    

    
    # Table data and styles
    interns = Intern.objects.all()
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
    title = _("Employees Details")
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

def add_intern(request):
    form = AddInternForm()
    departments = Department.objects.all()
    services = Service.objects.all()
    context = {
        "form": form,
        "departments": departments,
        "services" : services
    }
    return render(request, 'hod_template/add_intern_template.html', context)




def add_intern_save(request):
    if request.method != "POST":
        messages.error(request, _("Invalid Method"))
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
            session_year_id = int(form.cleaned_data['session_year_id'])
            department_id = int(form.cleaned_data['department_id'])
            service_id = int(form.cleaned_data['service_id'])
            gender = form.cleaned_data['gender']
            num_tel = form.cleaned_data['num_tel']
            
            print(department_id)
            print(type(department_id))

            print(service_id)
            print(type(service_id))

            print(session_year_id)
            print(type(session_year_id))

            department_obj = Department.objects.get(id=department_id)
            print(department_obj)
            print(type(department_obj))

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
                user_type = CustomUser.EMAIL_TO_USER_TYPE_MAP['intern']
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type= user_type)
                user.intern.address = address

                department_obj = Department.objects.get(id=department_id)
                print(department_obj)
                user.intern.department_id = department_obj

                service_obj = Service.objects.get(id=service_id)
                print(service_obj)
                user.intern.service_id = service_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.intern.session_year_id = session_year_obj

                user.intern.gender = gender

                user.intern.numero_telephone = num_tel
                user.intern.profile_pic = profile_pic_url
                user.save()
                messages.success(request, _("Employee Added Successfully!"))
                return redirect('add_intern')
            except Exception as e :
                print(e)
                messages.error(request, _("Failed to Add Employee!"))
                return redirect('add_intern')
            except Department.DoesNotExist:
                print("Department not found.")
            except Service.DoesNotExist:
                print("Service not found.")
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
    form.fields['service_id'].initial = intern.service_id.id
    form.fields['gender'].initial = intern.gender
    form.fields['session_year_id'].initial = intern.session_year_id.id
    form.fields['num_tel'].initial = intern.numero_telephone

    departments = Department.objects.all()
    services = Service.objects.all()
    context = {
        "id": intern_id,
        "username": intern.admin.username,
        "form": form,
        "departments": departments,
        "services" : services,
    }
    return render(request, "hod_template/edit_intern_template.html", context)


def edit_intern_save(request):
    if request.method != "POST":
        return HttpResponse(_("Invalid Method!"))
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
            service_id = form.cleaned_data['service_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']
            num_tel = form.cleaned_data['num_tel']

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

                service = Service.objects.get(id=service_id)
                intern_model.service_id = service

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                intern_model.session_year_id = session_year_obj

                intern_model.gender = gender
                intern_model.numero_telephone = num_tel
                if profile_pic_url != None:
                    intern_model.profile_pic = profile_pic_url
                intern_model.save()
                # Delete intern_id SESSION after the data is updated
                del request.session['intern_id']

                messages.success(request, _("Employee Updated Successfully!"))
                return redirect('/edit_intern/'+intern_id)
            except:
                messages.success(request, _("Failed to Update Employee."))
                return redirect('/edit_intern/'+intern_id)
        else:
            return redirect('/edit_intern/'+intern_id)


def delete_intern(request, intern_id):
    intern = Intern.objects.get(admin=intern_id)
    try:
        intern.delete()
        messages.success(request, _("Employee Deleted Successfully."))
        return redirect('manage_intern')
    except:
        messages.error(request, _("Failed to Delete Employee."))
        return redirect('manage_intern')



def generate_assignment_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    file_name = "assignments_details.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Create a SimpleDocTemplate instance
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Table data and styles
    assignments = Headquarter.objects.all()
    table_data = [[_("Assignment Name"), _("Department"), _("Service"), _("Start Period"), _("End Period"), _("Staff")]]

    for assignment in assignments:
        # Combine last name and email in one cell with inline styles
        full_name_staff = f"<b>{assignment.headquarter_name}</b>"
        row = [
            
            
            Paragraph(full_name_staff, getSampleStyleSheet()["BodyText"]),
            Paragraph(assignment.department_id.department_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(assignment.service_id.service_name, getSampleStyleSheet()["BodyText"]),
            Paragraph(str(assignment.session_year_id.session_start_year), getSampleStyleSheet()["BodyText"]),
            Paragraph(str(assignment.session_year_id.session_end_year), getSampleStyleSheet()["BodyText"]),
            Paragraph(assignment.staff_id.username, getSampleStyleSheet()["BodyText"])  # Use BodyText style for inline formatting
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
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    response.write(pdf)

    return response


def add_headquarter(request):
    departments = Department.objects.all()
    services = Service.objects.all()
    staffs = CustomUser.objects.filter(user_type= CustomUser.STAFF)
    
    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        
        for session_year in session_years:
            translated_text = _(' to ')
            session_text = f"{str(session_year.session_start_year)}{translated_text}{str(session_year.session_end_year)}"
            single_session_year = (session_year.id, session_text)
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []

    context = {
        "departments": departments,
        "services" : services,
        "staffs": staffs,
        "session_year_list": session_year_list
    }
    return render(request, 'hod_template/add_headquarter_template.html', context)



def add_headquarter_save(request):
    if request.method != "POST":
        messages.error(request, _("Method Not Allowed!"))
        return redirect('add_headquarter')
    else:
        headquarter_name = request.POST.get('headquarter')
        print(headquarter_name)
        department_id = request.POST.get('department')
        
        department = Department.objects.get(id=department_id)
        print(department)

        service_id = request.POST.get('service')
        service = Service.objects.get(id=service_id)
        print(service)

        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        session_year_id = request.POST.get('session_year')
        session_year = SessionYearModel.objects.get(id=session_year_id)
        
        
        try:
            
            headquarterN = Headquarter(headquarter_name=headquarter_name, department_id=department, service_id=service, staff_id=staff, session_year_id=session_year)
            headquarterN.save()
            messages.success(request, _("Assignment Added Successfully!"))
            return redirect('add_headquarter')
        except Exception as e:
            print("Error:", e)
            messages.error(request, _("Failed to Add Assignment!"))
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
    services = Service.objects.all()
    staffs = CustomUser.objects.filter(user_type=CustomUser.STAFF)
    context = {
        "headquarter": headquarter,
        "departments": departments,
        "services": services,
        "staffs": staffs,
        "id": headquarter_id
    }
    return render(request, 'hod_template/edit_headquarter_template.html', context)


def edit_headquarter_save(request):
    if request.method != "POST":
        HttpResponse(_("Invalid Method."))
    else:
        headquarter_id = request.POST.get('headquarter_id')
        headquarter_name = request.POST.get('headquarter')
        department_id = request.POST.get('department')
        service_id = request.POST.get('service')
        staff_id = request.POST.get('staff')

        try:
            headquarter = Headquarter.objects.get(id=headquarter_id)
            headquarter.headquarter_name = headquarter_name

            department = Department.objects.get(id=department_id)
            headquarter.department_id = department

            service = Service.objects.get(id=service_id)
            headquarter.service_id = service

            staff = CustomUser.objects.get(id=staff_id)
            headquarter.staff_id = staff
            
            headquarter.save()

            messages.success(request, _("Assignment Updated Successfully."))
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_headquarter", kwargs={"headquarter_id":headquarter_id}))

        except:
            messages.error(request, _("Failed to Update Assignment."))
            return HttpResponseRedirect(reverse("edit_headquarter", kwargs={"headquarter_id":headquarter_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_headquarter(request, headquarter_id):
    headquarter = Headquarter.objects.get(id=headquarter_id)
    try:
        headquarter.delete()
        messages.success(request, _("Assignment Deleted Successfully."))
        return redirect('manage_headquarter')
    except:
        messages.error(request, _("Failed to Delete Assignment."))
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

def generate_view_admin_message_employees_pdf(request):
    emp = request.user
    response = HttpResponse(content_type='application/pdf')
    file_name = "messages_apply_by_employees.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    feedback_data = FeedBackIntern.objects.all()

    table_data = [[_("Message"), _("Message Reply"), _("Sended On")]]
    
    for fed in feedback_data:
        
        row = [

            Paragraph(str(fed.feedback), getSampleStyleSheet()["BodyText"]),
            Paragraph(fed.feedback_reply, getSampleStyleSheet()["BodyText"]),  # Use BodyText style for inline formatting
            Paragraph(str(fed.created_at.strftime("%Y-%m-%d %H:%M:%S")), getSampleStyleSheet()["BodyText"]),
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
    title = _('Messages Apply by Employees')
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

def generate_messages_staff_pdf(request):
    
    response = HttpResponse(content_type='application/pdf')
    file_name = "messages_staffs.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    feedback_data = FeedBackStaffs.objects.all()

    table_data = [[_("Staff Name"), _("Message"), _("Sended On"), _("Message Reply")]]
    
    for fed in feedback_data:
        
        name = f'<b>{fed.staff_id.admin.first_name} {fed.staff_id.admin.last_name}</b>'
        row = [

            Paragraph(name, getSampleStyleSheet()["BodyText"]),
            Paragraph(str(fed.feedback), getSampleStyleSheet()["BodyText"]),
            Paragraph(str(fed.created_at.strftime("%Y-%m-%d %H:%M:%S")), getSampleStyleSheet()["BodyText"]),
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
    title = _('Messages Apply by Staffs')
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

def generate_admin_view_leave_employee_pdf(request):
    
    response = HttpResponse(content_type='application/pdf')
    file_name = "leave_apply_by_employees.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    leave_data = LeaveReportIntern.objects.all()

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
    title = _('Leaves Apply by Employees')
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


def generate_leaves_staffs_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    file_name = "leave_apply_by_staffs.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    leave_data = LeaveReportStaff.objects.all()

    table_data = [[_("Staff Name"), _("Leave Date"), _("Leave Message"), _("Status")]]
    
    for lev in leave_data:
        if lev.leave_status == 1:
            status = _('Approved')
        elif lev.leave_status == 2:
            status = _('Rejected')
        else:
            status = _('Pending')
        
        name = f'<b>{lev.staff_id.admin.first_name} {lev.staff_id.admin.last_name}</b>' 
        row = [
            
            Paragraph(name, getSampleStyleSheet()["BodyText"]),
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
    title = _('Leave Apply by Staffs')
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

def generate_admin_view_attendance_pdf(request):
    
    response = HttpResponse(content_type='application/pdf')
    file_name = "view_attendance.pdf"
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    

    # Create a new PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    

    interns = Intern.objects.all()
    
    
    
    table_data = [[_("Full Name"), _("Date"), _("Status")]]

    intern_totals = {}

    
    
    unique_combinations = set()

    unique_assignments = set()
    for inte in interns:

        attendance_data = AttendanceReport.objects.filter(intern_id=inte.id)

        

        # Variables to store totals
        unique_dates = set()
        total_present = 0
        total_absent = 0

        for intern in attendance_data:
          
          nameInter = f'<b>{intern.intern_id.admin.first_name} {intern.intern_id.admin.last_name}</b>'
          
          intern_attendance_tuple = (intern.intern_id.id, str(intern.attendance_id.attendance_date))
          assignment_attendance_tuple = (intern.attendance_id.headquarter_id.id, str(intern.attendance_id.headquarter_id))
          if intern_attendance_tuple in unique_combinations and assignment_attendance_tuple not in unique_assignments:
            # If not, add the tuple to the set and process the data
            unique_assignments.add(assignment_attendance_tuple)
            unique_combinations.add(intern_attendance_tuple)

          if intern_attendance_tuple not in unique_combinations:
            # If not, add the tuple to the set and process the data
            unique_combinations.add(intern_attendance_tuple)

            if intern.status is True:
              total_present += 1
              name = _('Present')
              
            elif intern.status is False:
              total_absent += 1
              name = _('Absent')
              
            else:
              name = _('None')
          
          
            row = [
            
             Paragraph(nameInter, getSampleStyleSheet()["BodyText"]),  # Use BodyText style for inline formatting  
            #  Paragraph(intern.attendance_id.headquarter_id.headquarter_name, getSampleStyleSheet()["BodyText"]),   
             Paragraph(str(intern.attendance_id.attendance_date), getSampleStyleSheet()["BodyText"]),    
             Paragraph(name, getSampleStyleSheet()["BodyText"]),

            
            ]
            table_data.append(row)
        
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
    title = _('All Employees Attendance')
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


    # for intern_id, totals in intern_totals.items():
    #     intern_name = Intern.objects.get(id=intern_id).admin.first_name +" "+ Intern.objects.get(id=intern_id).admin.last_name
    #     elements.append(Paragraph(_("Total Days for {}: ").format(intern_name) + str(totals['total_days']), getSampleStyleSheet()["BodyText"]))
    #     elements.append(Paragraph(_("Total {} Present: ").format(intern_name) + str(totals['total_present']), getSampleStyleSheet()["BodyText"]))
    #     elements.append(Paragraph(_("Total {} Absent: ").format(intern_name) + str(totals['total_absent']), getSampleStyleSheet()["BodyText"]))
    #     elements.append(Spacer(0, 10))
    #     elements.append(Paragraph("-------------------------------------------------", getSampleStyleSheet()["BodyText"])),
   
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
def admin_get_attendance_dates(request):
    
    headquarter_id = request.POST.get("headquarter")
    session_year = request.POST.get("session_year_id")

    
    headquarter_model = Headquarter.objects.get(id=headquarter_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    
    attendance = Attendance.objects.filter(headquarter_id=headquarter_model, session_year_id=session_model)

  
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_intern(request):
    
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    
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
        messages.error(request, _("Invalid Method!"))
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
            messages.success(request, _("Profile Updated Successfully"))
            return redirect('admin_profile')
        except:
            messages.error(request, _("Failed to Update Profile"))
            return redirect('admin_profile')


def staff_profile(request):
    pass


def intern_profile(request):
    pass

