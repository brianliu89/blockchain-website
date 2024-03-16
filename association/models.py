from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

NEWS_TYPE = (('協會消息', '協會消息'), ('會員消息', '會員消息'))
RESOURCE_TYPE = (('學研', '學研'), ('廠商', '廠商'))
GROUP = (('法規調適組', '法規調適組'), ('應用推廣組', '應用推廣組'), ('產學合作組', '產學合作組'))


# Create your models here.
class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=20)
    name = models.CharField(max_length=20, null=True)
    id_number = models.CharField(max_length=10, null=True)
    phone = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length=50, null=True)
    attendance = models.IntegerField(default=0)
    is_company = models.BooleanField(default=False)


class Company(models.Model):
    my_user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=10,  null=True)
    founder = models.CharField(max_length=10, null=True)
    intro = models.CharField(max_length=200, null=True)
    service = models.CharField(max_length=200, null=True)
    milestone = models.CharField(max_length=300, null=True)
    link = models.CharField(max_length=200,  null=True)
    group = models.CharField(max_length=10, choices=GROUP, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class News(models.Model):
    title = models.CharField(max_length=50)
    content = RichTextUploadingField()
    image = models.ImageField(upload_to='%Y/%m/', null=True)
    type = models.CharField(max_length=11, choices=NEWS_TYPE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    # en_title = models.CharField(max_length=50)
    # en_content = RichTextUploadingField()
    # en_image = models.ImageField(upload_to='%Y/%m/', null=True)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return '/static/img/home-bg.jpg'


class Course(models.Model):
    image = models.ImageField(upload_to='%Y/%m/', null=True)
    course_name = models.CharField(max_length=50, null=True)
    project_name = models.CharField(max_length=50, null=True)
    permit_number = models.CharField(max_length=20, null=True)
    adviser = models.CharField(max_length=30, null=True)
    organizer = models.CharField(max_length=30, null=True)
    registration_date = models.CharField(max_length=20, null=True)
    venue = models.CharField(max_length=30, null=True)
    enrollment = models.CharField(max_length=20, null=True)
    training_cost = models.CharField(max_length=20, null=True)
    training_date = models.CharField(max_length=20, null=True)
    training_time = models.CharField(max_length=20, null=True)
    link = models.CharField(max_length=200,  null=True)
    content = models.CharField(max_length=500, null=True)
    gender = models.CharField(max_length=5, null=True)
    education = models.CharField(max_length=20, null=True)
    age = models.CharField(max_length=5, null=True)
    military_service = models.CharField(max_length=20, null=True)
    skill = models.CharField(max_length=100, null=True)
    condition = models.CharField(max_length=100, null=True)
    remark = models.CharField(max_length=100, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return '/static/img/home-bg.jpg'


class CourseMessage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default='訪客')
    message = models.CharField(max_length=100)
    reply = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Resource(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=10, null=True)
    organization = models.CharField(max_length=30, null=True)
    period = models.CharField(max_length=20, null=True)
    qualification = models.CharField(max_length=50, null=True)
    link = models.CharField(max_length=200,  null=True)
    type = models.CharField(max_length=5, choices=RESOURCE_TYPE, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    # en_name = models.CharField(max_length=50)
    # en_category = models.CharField(max_length=30, null=True)
    # en_organization = models.CharField(max_length=30, null=True)
    # en_period = models.CharField(max_length=20, null=True)
    # en_qualification = models.CharField(max_length=30, null=True)
    # en_link = models.URLField(max_length=200, null=True)


class Message(models.Model):
    my_user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    reply = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Intro(models.Model):
    intro = RichTextUploadingField()
