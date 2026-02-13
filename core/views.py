from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import StudentRegisterForm, TeacherRegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import StatusUpdateForm
from .models import StatusUpdate
from .models import Course, Enrollment
from .forms import CourseForm
from django.http import HttpResponseForbidden
from .forms import FeedbackForm
from django.urls import reverse
from .models import Notification
from django.db.models import Q,Exists, OuterRef
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import CourseBlock
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone



def register_student(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student account created. Please log in.")
            return redirect('login')
    else:
        form = StudentRegisterForm()
    return render(request, 'core/register_student.html', {'form': form, 'user_type': 'Student'})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher account created. Please log in.")
            return redirect('login')
    else:
        form = TeacherRegisterForm()
    return render(request, 'core/register_teacher.html', {'form': form, 'user_type': 'Teacher'})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_home(request):
    now = timezone.now()
    window_start = now - timedelta(days=1)

    # Optional: remove this user's old statuses (> 24h) so the table stays tidy
    StatusUpdate.objects.filter(user=request.user, created_at__lt=window_start).delete()

    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data.get('content', '').strip()

            # Check if the user already has a status in the last 24h
            existing = (
                StatusUpdate.objects
                .filter(user=request.user, created_at__gte=window_start)
                .order_by('-created_at')
                .first()
            )

            if existing:
                # Update existing status
                existing.content = content
                existing.created_at = now  # keep it fresh / move to top
                existing.save()
                messages.success(request, "Your status was updated.")
            else:
                # Create a new one
                status = form.save(commit=False)
                status.user = request.user
                status.save()
                messages.success(request, "Your status was posted.")
            return redirect('home')
    else:
        form = StatusUpdateForm()

    # Only show the last 24h of updates (you can keep it as a list or just show the latest)
    user_statuses = (
        StatusUpdate.objects
        .filter(user=request.user, created_at__gte=window_start)
        .order_by('-created_at')
    )

    return render(request, 'core/home.html', {
        'user': request.user,
        'form': form,
        'statuses': user_statuses,
    })

@login_required
def create_course(request):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not authorized to create courses.")

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            if course.materials:    
                # notify enrolled students
                student_ids = Enrollment.objects.filter(course=course).values_list('student_id', flat=True)
                Notification.objects.bulk_create([
                    Notification(recipient_id=sid,  
                        message=f"New material added in {course.title}.",
                        link=reverse('course_detail', args=[course.id]))
                    for sid in student_ids
    ])
            messages.success(request, f"Course '{course.title}' created successfully.")
            messages.info(request, f"Enrolled students will be notified when materials are added.")
            return redirect('my_courses')
    else:
        form = CourseForm()

    return render(request, 'core/create_course.html', {'form': form})

@login_required
def my_courses(request):
    if request.user.is_teacher:
        courses = Course.objects.filter(teacher=request.user).prefetch_related('enrollments__student')
    else:
        courses = [en.course for en in Enrollment.objects.filter(student=request.user)]
    return render(request, 'core/my_courses.html', {'courses': courses})

@login_required
def course_list(request):
    courses = Course.objects.exclude(enrollments__student=request.user)
    return render(request, 'core/course_list.html', {'courses': courses})

@login_required
def remove_student(request, course_id, student_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("Only teachers can remove students.")
    
    try:
        course = Course.objects.get(id=course_id, teacher=request.user)
        enrolment = Enrollment.objects.get(course=course, student_id=student_id)
        enrolment.delete()
    except Course.DoesNotExist:
        return HttpResponseForbidden("You do not own this course.")
    except Enrollment.DoesNotExist:
        pass  

    return redirect('my_courses')

@login_required
def leave_feedback(request, course_id):
    course = Course.objects.get(id=course_id)
    
    # Must be enrolled to give feedback
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponseForbidden("You are not enrolled in this course.")

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.course = course
            feedback.save()
            return redirect('my_courses')
    else:
        form = FeedbackForm()

    return render(request, 'core/leave_feedback.html', {'form': form, 'course': course})

from .models import CourseBlock 
@login_required
def enroll_in_course(request, course_id):
    course = Course.objects.get(id=course_id)
    
    #block check
    if CourseBlock.objects.filter(course=course, student=request.user).exists():
        messages.error(request, "You are blocked from this course.")
        return redirect('course_list')


    enrolment, created = Enrollment.objects.get_or_create(
        student=request.user, 
        course=course
      )

    if created and not request.user.is_teacher:
            messages.success(request, f'You have enrolled in {course.title}.')
            # Notify teacher only if a student enrolls

            # create a notification for the teacher
            Notification.objects.create(
                recipient=course.teacher,
                message=f"{request.user.username} enrolled in {course.title}.",
                link=reverse('my_courses')  # or a course detail page if you add one
            )
            # teacher = course.teacher
            # messages.info(request, f'Notification sent to {teacher.username} (simulated).')

    return redirect('my_courses')

@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('home')

@login_required
def course_chat(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return HttpResponseForbidden("Course not found.")
    # access control: teacher or enrolled student
    if not (course.teacher_id == request.user.id or
            Enrollment.objects.filter(course=course, student=request.user).exists()):
        return HttpResponseForbidden("You are not allowed in this chat.")
    return render(request, "core/course_chat.html", {"course": course})

User = get_user_model()
@login_required
def search_users(request):
    if not request.user.is_teacher:
        return HttpResponseForbidden("Only teachers can search users.")

    q = request.GET.get("q", "").strip()
    role = request.GET.get("role", "all")  # 'students' | 'teachers' | 'all'
    exblk = request.GET.get("exclude_blocked", "1") # default: exclude blocked
    exclude_blocked = exblk == "1"

    qs = User.objects.all().order_by("username")

    if role == "students":
        qs = qs.filter(is_teacher=False)
    elif role == "teachers":
        qs = qs.filter(is_teacher=True)

    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
     # Mark whether each user is blocked in ANY course taught by this teacher
    blocked_subq = CourseBlock.objects.filter(
        course__teacher=request.user,
        student_id=OuterRef("pk"),
    )
    qs = qs.annotate(is_blocked=Exists(blocked_subq))

    # Optionally exclude blocked users
    if exclude_blocked:
        qs = qs.filter(is_blocked=False)


    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/search.html", {
        "q": q,
        "role": role,
        "page_obj": page_obj,
        "exclude_blocked": exclude_blocked,
    })

    
@login_required
@require_POST
def block_student(request, course_id, student_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("Only teachers can block students.")
    try:
        course = Course.objects.get(id=course_id, teacher=request.user)
    except Course.DoesNotExist:
        return HttpResponseForbidden("You do not own this course.")

    # create block
    CourseBlock.objects.get_or_create(course=course, student_id=student_id)
    # remove if currently enrolled
    Enrollment.objects.filter(course=course, student_id=student_id).delete()
    messages.info(request, "Student blocked and removed from course.")
    return redirect('my_courses')

@login_required
@require_POST
def unblock_student(request, course_id, student_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("Only teachers can unblock students.")
    try:
        course = Course.objects.get(id=course_id, teacher=request.user)
    except Course.DoesNotExist:
        return HttpResponseForbidden("You do not own this course.")

    CourseBlock.objects.filter(course=course, student_id=student_id).delete()
    messages.success(request, "Student unblocked.")
    return redirect('my_courses')

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # access policy: anyone who can see it (students or teacher).
    # If you want to restrict to teacher + enrolled students only, uncomment:
    # if not (course.teacher_id == request.user.id or Enrollment.objects.filter(course=course, student=request.user).exists()):
    #     return HttpResponseForbidden("You are not allowed to view this course.")
    feedbacks = course.feedbacks.select_related('student').order_by('-created_at')
    enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()
    return render(request, "core/course_detail.html", {
        "course": course,
        "feedbacks": feedbacks,
        "enrolled": enrolled,
    })