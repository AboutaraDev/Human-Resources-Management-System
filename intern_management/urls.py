
from django.urls import path, include
from . import views, HodViews, StaffViews, InternViews

from django.utils.translation import gettext_lazy as _


urlpatterns = [
    path('', views.loginPage, name='login'),
    path(_('doLogin/'), views.doLogin, name="doLogin"),
    path(_('get_user_details/'), views.get_user_details, name="get_user_details"),
    path(_('logout_user/'), views.logout_user, name="logout_user"),
    path(_('admin_home/'), HodViews.admin_home, name="admin_home"),
    path(_('admin_profile/'), HodViews.admin_profile, name="admin_profile"),
    path(_('admin_profile_update/'), HodViews.admin_profile_update, name="admin_profile_update"),
  
   
    path(_('add_staff/'), HodViews.add_staff, name="add_staff"),
    path(_('manage_staff/'), HodViews.manage_staff, name="manage_staff"),
    path(_('add_staff_save/'), HodViews.add_staff_save, name="add_staff_save"),
    path(_('edit_staff/<staff_id>/'), HodViews.edit_staff, name="edit_staff"),
    path(_('edit_staff_save/'), HodViews.edit_staff_save, name="edit_staff_save"),
    path(_('delete_staff/<staff_id>/'), HodViews.delete_staff, name="delete_staff"),

    path(_('add_department/'), HodViews.add_department, name="add_department"),
    path(_('add_department_save/'), HodViews.add_department_save, name="add_department_save"),
    path(_('manage_department/'), HodViews.manage_department, name="manage_department"),
    path(_('edit_department/<department_id>/'), HodViews.edit_department, name="edit_department"),
    path(_('edit_department_save/'), HodViews.edit_department_save, name="edit_department_save"),
    path(_('delete_department/<department_id>/'), HodViews.delete_department, name="delete_department"),

    
    path(_('manage_session/'), HodViews.manage_session, name="manage_session"),
    path(_('add_session/'), HodViews.add_session, name="add_session"),
    path(_('add_session_save/'), HodViews.add_session_save, name="add_session_save"),
    path(_('edit_session/<session_id>'), HodViews.edit_session, name="edit_session"),
    path(_('edit_session_save/'), HodViews.edit_session_save, name="edit_session_save"),
    path(_('delete_session/<session_id>/'), HodViews.delete_session, name="delete_session"),

    path(_('manage_intern/'), HodViews.manage_intern, name="manage_intern"),
    path(_('add_intern/'), HodViews.add_intern, name="add_intern"),
    path(_('add_intern_save/'), HodViews.add_intern_save, name="add_intern_save"),
    path(_('edit_intern/<intern_id>'), HodViews.edit_intern, name="edit_intern"),
    path(_('edit_intern_save/'), HodViews.edit_intern_save, name="edit_intern_save"),
    path(_('delete_intern/<intern_id>/'), HodViews.delete_intern, name="delete_intern"),

    path(_('manage_headquarter/'), HodViews.manage_headquarter, name="manage_headquarter"),
    path(_('add_headquarter/'), HodViews.add_headquarter, name="add_headquarter"),
    path(_('add_headquarter_save/'), HodViews.add_headquarter_save, name="add_headquarter_save"),
    path(_('edit_headquarter/<headquarter_id>'), HodViews.edit_headquarter, name="edit_headquarter"),
    path(_('edit_headquarter_save/'), HodViews.edit_headquarter_save, name="edit_headquarter_save"),
    path(_('delete_headquarter/<headquarter_id>/'), HodViews.delete_headquarter, name="delete_headquarter"),

    path(_('intern_feedback_message/'), HodViews.intern_feedback_message, name="intern_feedback_message"),
    path(_('intern_feedback_message_reply/'), HodViews.intern_feedback_message_reply, name="intern_feedback_message_reply"),
    path(_('staff_feedback_message/'), HodViews.staff_feedback_message, name="staff_feedback_message"),
    path(_('staff_feedback_message_reply/'), HodViews.staff_feedback_message_reply, name="staff_feedback_message_reply"),
    path(_('intern_leave_view/'), HodViews.intern_leave_view, name="intern_leave_view"),
    path(_('intern_leave_approve/<leave_id>/'), HodViews.intern_leave_approve, name="intern_leave_approve"),
    path(_('intern_leave_reject/<leave_id>/'), HodViews.intern_leave_reject, name="intern_leave_reject"),
    path(_('staff_leave_view/'), HodViews.staff_leave_view, name="staff_leave_view"),
    path(_('staff_leave_approve/<leave_id>/'), HodViews.staff_leave_approve, name="staff_leave_approve"),
    path(_('staff_leave_reject/<leave_id>/'), HodViews.staff_leave_reject, name="staff_leave_reject"),
    path(_('admin_view_attendance/'), HodViews.admin_view_attendance, name="admin_view_attendance"),
    path(_('admin_get_attendance_dates/'), HodViews.admin_get_attendance_dates, name="admin_get_attendance_dates"),
    path(_('admin_get_attendance_intern/'), HodViews.admin_get_attendance_intern, name="admin_get_attendance_intern"),
    path(_('admin_profile/'), HodViews.admin_profile, name="admin_profile"),
    path(_('admin_profile_update/'), HodViews.admin_profile_update, name="admin_profile_update"),

    # URLS FOR Staff
    path(_('staff_home/'), StaffViews.staff_home, name="staff_home"),
    path(_('staff_take_attendance/'), StaffViews.staff_take_attendance, name="staff_take_attendance"),
    path(_('get_interns/'), StaffViews.get_interns, name="get_interns"),
    path(_('save_attendance_data/'), StaffViews.save_attendance_data, name="save_attendance_data"),
    path(_('staff_update_attendance/'), StaffViews.staff_update_attendance, name="staff_update_attendance"),
    path(_('get_attendance_dates/'), StaffViews.get_attendance_dates, name="get_attendance_dates"),
    path(_('get_attendance_intern/'), StaffViews.get_attendance_intern, name="get_attendance_intern"),
    path(_('update_attendance_data/'), StaffViews.update_attendance_data, name="update_attendance_data"),
    path(_('staff_apply_leave/'), StaffViews.staff_apply_leave, name="staff_apply_leave"),
    path(_('staff_apply_leave_save/'), StaffViews.staff_apply_leave_save, name="staff_apply_leave_save"),
    path(_('staff_feedback/'), StaffViews.staff_feedback, name="staff_feedback"),
    path(_('staff_feedback_save/'), StaffViews.staff_feedback_save, name="staff_feedback_save"),
    path(_('staff_profile/'), StaffViews.staff_profile, name="staff_profile"),
    path(_('staff_profile_update/'), StaffViews.staff_profile_update, name="staff_profile_update"),
    path(_('staff_add_result/'), StaffViews.staff_add_result, name="staff_add_result"),
    path(_('staff_add_result_save/'), StaffViews.staff_add_result_save, name="staff_add_result_save"),
    path(_('view_headquarter/'), StaffViews.view_headquarter, name="view_headquarter"),
    path(_('view_intern/'), StaffViews.view_intern, name="view_intern"),
    path(_('intern_view_result_by_staff/'), StaffViews.intern_view_result_by_staff, name="intern_view_result_by_staff"),
    
     # URSL for Interns
    path(_('intern_home/'), InternViews.intern_home, name="intern_home"),
    path(_('intern_view_attendance/'), InternViews.intern_view_attendance, name="intern_view_attendance"),
    path(_('intern_view_attendance_post/'), InternViews.intern_view_attendance_post, name="intern_view_attendance_post"),
    path(_('intern_apply_leave/'), InternViews.intern_apply_leave, name="intern_apply_leave"),
    path(_('intern_apply_leave_save/'), InternViews.intern_apply_leave_save, name="intern_apply_leave_save"),
    path(_('intern_feedback/'), InternViews.intern_feedback, name="intern_feedback"),
    path(_('intern_feedback_save/'), InternViews.intern_feedback_save, name="intern_feedback_save"),
    path(_('intern_profile/'), InternViews.intern_profile, name="intern_profile"),
    path(_('intern_profile_update/'), InternViews.intern_profile_update, name="intern_profile_update"),
    path(_('intern_view_result/'), InternViews.intern_view_result, name="intern_view_result"),
    path(_('intern_view_headquarters/'), InternViews.intern_view_headquarters, name="intern_view_headquarters"),


    path(_('check_email_exist/'), HodViews.check_email_exist, name="check_email_exist"),
    path(_('check_username_exist/'), HodViews.check_username_exist, name="check_username_exist"),

]