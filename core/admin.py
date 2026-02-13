from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Course, Enrollment, Feedback, StatusUpdate

admin.site.register(User)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Feedback)
admin.site.register(StatusUpdate)
