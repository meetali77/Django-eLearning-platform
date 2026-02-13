from django.urls import path
from . import views

urlpatterns = [
    path('register/student/', views.register_student, name='register_student'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.user_home, name='home'),  
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/my/', views.my_courses, name='my_courses'),
    path('courses/enrol/<int:course_id>/', views.enroll_in_course, name='enroll_in_course'),
    path('courses/<int:course_id>/remove/<int:student_id>/', views.remove_student, name='remove_student'),
    path('courses/<int:course_id>/feedback/', views.leave_feedback, name='leave_feedback'),
    path('notifications/mark-read/',views.mark_notifications_read, name='mark_notifications_read'),
    path("courses/<int:course_id>/chat/", views.course_chat, name="course_chat"),
    path("search/", views.search_users, name="search_users"),
    path('courses/<int:course_id>/block/<int:student_id>/', views.block_student, name='block_student'),
    path('courses/<int:course_id>/unblock/<int:student_id>/', views.unblock_student, name='unblock_student'),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),



]




