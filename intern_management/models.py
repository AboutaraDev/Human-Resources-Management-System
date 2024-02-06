from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.

class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    objects = models.Manager()


class CustomUser(AbstractUser):

    
    HOD = '1'
    STAFF = '2'
    INTERN = '3'
    
    EMAIL_TO_USER_TYPE_MAP = {
        'hod': HOD,
        'staff': STAFF,
        'intern': INTERN
    }
    user_type_data = ((HOD, 'HOD'), (STAFF, 'Staff'), (INTERN, 'Intern'))
    user_type = models.CharField(default='1', choices=user_type_data,max_length=10)


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    address = models.TextField(_('address'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    address = models.TextField(_('address'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    department_name = models.CharField(_('department name'),max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.department_name

  

class Service(models.Model):
    id = models.AutoField(primary_key=True)
    service_name = models.CharField(_('service name'), max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='services')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



     
class Headquarter(models.Model):
    id = models.AutoField(primary_key=True)
    headquarter_name = models.CharField(_('assignment name'), max_length=255)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE, default=2)
    service_id = models.ForeignKey(Service, on_delete=models.CASCADE)
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

def get_default_session_year_id():
     try:
        default_session_year = SessionYearModel.objects.earliest('session_start_year')
        return default_session_year.id
     except SessionYearModel.DoesNotExist:
        return None

    
class Intern(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(_('gender'),max_length=50)
    profile_pic = models.FileField(_('profile picture'))
    address = models.TextField()
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    service_id = models.ForeignKey(Service, on_delete=models.CASCADE, default=1)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    numero_telephone = models.CharField(_('phone number'), max_length=20)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = models.Manager()

    

class Attendance(models.Model):
    # headquarter Attendance
    id = models.AutoField(primary_key=True)
    headquarter_id = models.ForeignKey(Headquarter, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class AttendanceReport(models.Model):
    # Individual Intern Attendance
    id = models.AutoField(primary_key=True)
    intern_id = models.ForeignKey(Intern, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class LeaveReportIntern(models.Model):
    id = models.AutoField(primary_key=True)
    intern_id = models.ForeignKey(Intern, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField(_('leave message'))
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(_('leave date'),max_length=255)
    leave_message = models.TextField(_('leave message'))
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackIntern(models.Model):
    id = models.AutoField(primary_key=True)
    intern_id = models.ForeignKey(Intern, on_delete=models.CASCADE)
    feedback = models.TextField(_('feedback'))
    feedback_reply = models.TextField(_('feedback reply'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField(_('feedback'))
    feedback_reply = models.TextField(_('feedback reply'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class NotificationIntern(models.Model):
    id = models.AutoField(primary_key=True)
    intern_id = models.ForeignKey(Intern, on_delete=models.CASCADE)
    message = models.TextField(_('message'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    stafff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField(_('message'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class InternResult(models.Model):
    id = models.AutoField(primary_key=True)
    intern_id = models.ForeignKey(Intern, on_delete=models.CASCADE)
    headquarter_id = models.ForeignKey(Headquarter, on_delete=models.CASCADE)
    # headquarter_exam_marks = models.FloatField(default=0)
    headquarter_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in HOD, Staff or Intern
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == CustomUser.HOD:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == CustomUser.STAFF:
            Staffs.objects.create(admin=instance)
        if instance.user_type == CustomUser.INTERN:
            Intern.objects.create(admin=instance, department_id=Department.objects.get(id=1), session_year_id=SessionYearModel.objects.get(id=1), address="", profile_pic="", gender="")
    

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == CustomUser.HOD:
        instance.adminhod.save()
    if instance.user_type == CustomUser.STAFF:
        instance.staffs.save()
    if instance.user_type == CustomUser.INTERN:
        instance.intern.save()