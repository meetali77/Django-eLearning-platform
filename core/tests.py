from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Course, Enrollment, Feedback

User = get_user_model()


class BaseData(TestCase):
    @classmethod
    def setUpTestData(cls):
        # One teacher and two students used by all tests
        cls.teacher = User.objects.create_user(
            username="teach1", password="pass123", is_teacher=True
        )
        cls.student1 = User.objects.create_user(
            username="stud1", password="pass123", is_teacher=False
        )
        cls.student2 = User.objects.create_user(
            username="stud2", password="pass123", is_teacher=False
        )


class CourseModelTest(BaseData):
    def test_course_creation(self):
        course = Course.objects.create(
            title="Math 101",
            description="Basics",
            teacher=self.teacher,
        )
        self.assertEqual(course.title, "Math 101")
        # If you defined __str__ to show title:
        self.assertEqual(str(course), "Math 101")
        # The FK is correctly set
        self.assertEqual(course.teacher, self.teacher)


class EnrollmentModelTest(BaseData):
    def setUp(self):
        self.course = Course.objects.create(
            title="Science", description="Physics", teacher=self.teacher
        )

    def test_enrollment_creation(self):
        enr = Enrollment.objects.create(student=self.student1, course=self.course)
        self.assertEqual(enr.course, self.course)
        self.assertEqual(enr.student, self.student1)

    def test_enrollment_is_unique_per_student_course(self):
        Enrollment.objects.create(student=self.student1, course=self.course)
        with self.assertRaises(Exception):
            # If your model has unique_together('student','course') or a constraint,
            # the second create should error.
            Enrollment.objects.create(student=self.student1, course=self.course)


class FeedbackModelTest(BaseData):
    def setUp(self):
        self.course = Course.objects.create(
            title="History", description="Ancient times", teacher=self.teacher
        )

    def test_feedback_creation(self):
        fb = Feedback.objects.create(
            course=self.course, student=self.student2, text="Great course!"
        )
        self.assertEqual(fb.text, "Great course!")
        self.assertEqual(fb.course, self.course)
        self.assertEqual(fb.student, self.student2)

