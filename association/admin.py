from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import MyUser, Company, News, Course, CourseMessage, Resource, Message, Intro


class MemberInline(admin.StackedInline):
    model = MyUser
    can_delete = False
    verbose_name_plural = "MyUser"


class UserAdmin(BaseUserAdmin):
    inlines = (MemberInline,)


# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(MyUser)
admin.site.register(Company)
admin.site.register(News)
admin.site.register(Course)
admin.site.register(CourseMessage)
admin.site.register(Resource)
admin.site.register(Message)
admin.site.register(Intro)
