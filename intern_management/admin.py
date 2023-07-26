from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, AdminHOD, Staffs, Department, Headquarter, Intern, Attendance, AttendanceReport, LeaveReportIntern, LeaveReportStaff, FeedBackIntern, FeedBackStaffs, NotificationIntern, NotificationStaffs


# Register your models here.

class UserModel(UserAdmin):
    pass

admin.site.register(CustomUser, UserModel)


admin.site.register(AdminHOD)
admin.site.register(Staffs)
admin.site.register(Department)
admin.site.register(Headquarter)
admin.site.register(Intern)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportIntern)
admin.site.register(LeaveReportStaff)
admin.site.register(FeedBackIntern)
admin.site.register(FeedBackStaffs)
admin.site.register(NotificationIntern)
admin.site.register(NotificationStaffs)



