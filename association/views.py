from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View, generic
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.conf import settings
import re

from .models import MyUser, Company, News, Course, CourseMessage, Resource, Message, Intro
from .forms import NewsForm, IntroForm

email_re = r'^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$'
phone_re = r'\+?(\#|\*|\d)*'


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'association/index.html'
    context_object_name = 'assoc_news_list'

    def get_queryset(self):
        assoc_news_list = News.objects.filter(type='協會消息').order_by('-create_time')
        return assoc_news_list[:6] if assoc_news_list.count() > 6 else assoc_news_list

    def get_context_data(self, **kwargs):
        member_news_list = News.objects.filter(type='會員消息').order_by('-create_time')

        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'member_news_list': member_news_list[:6] if member_news_list.count() > 6 else member_news_list
        })
        return context


class NewsListView(generic.ListView):
    template_name = 'association/news_list.html'
    context_object_name = 'assoc_news_list'

    def get_queryset(self):
        return News.objects.filter(type='協會消息').order_by('-create_time')

    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        context.update({
            'member_news_list': News.objects.filter(type='會員消息').order_by('-create_time')
        })
        return context


class NewsArticleView(generic.DetailView):
    template_name = 'association/news_article.html'
    model = News
    context_object_name = 'article'


class IntroView(View):
    template_name = 'association/intro.html'

    def get(self, request, *args, **kwargs):
        intro = Intro.objects.all()[0]
        return render(request, self.template_name, {'intro': intro})


class CourseView(generic.ListView):
    template_name = 'association/course.html'
    context_object_name = 'course_list'
    paginate_by = 4

    def get_queryset(self):
        return Course.objects.order_by('-create_time')


class CourseDetailView(generic.DetailView):
    template_name = 'association/course_detail.html'
    model = Course
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        course = Course.objects.get(pk=self.kwargs.get('pk'))

        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context.update({
            'course_message_list': CourseMessage.objects.filter(course=course).order_by('-create_time')
        })
        return context


class AddCourseMessageView(View):
    template_name = 'association/course_detail.html'

    def get(self, request, *args, **kwargs):
        return redirect('course')

    def post(self, request, *args, **kwargs):
        id = request.POST['course_id']
        course = Course.objects.get(pk=id)
        course_message = request.POST['course_message'].strip()
        name = '訪客' if request.user.is_anonymous else request.user.myuser.name

        if not 0 < len(course_message) <= 100:
            return render(request, self.template_name, {'messages': ['留言長度需介於1~100字元'],
                                                        'course': course,
                                                        'course_message_list': CourseMessage.objects.filter(course=course).order_by('-create_time'),
                                                        'course_message': course_message})

        course.coursemessage_set.create(message=course_message, name=name)
        return redirect('/course_detail/' + id + '/')


class ReplyCourseMessageView(View):
    template_name = 'association/course_detail.html'

    def get(self, request, *args, **kwargs):
        return redirect('course')

    def post(self, request, *args, **kwargs):
        id = request.POST['course_message_id']
        course_id = request.POST['course_id']
        course_message = CourseMessage.objects.get(pk=id)
        reply = request.POST['reply']

        course_message.reply = reply
        course_message.status = True
        course_message.save()
        return redirect('/course_detail/' + course_id + '/')


class CompanyView(generic.ListView):
    template_name = 'association/company.html'
    model = Company
    context_object_name = 'company_list'


class CompanyDetailView(generic.DetailView):
    template_name = 'association/company_detail.html'
    model = Company
    context_object_name = 'company'


class ResourceView(generic.ListView):
    template_name = 'association/resource.html'
    context_object_name = 'study_resource_list'

    def get_queryset(self):
        return Resource.objects.filter(type='學研').order_by('-create_time')

    def get_context_data(self, **kwargs):
        context = super(ResourceView, self).get_context_data(**kwargs)
        context.update({
            'firm_resource_list': Resource.objects.filter(type='廠商').order_by('-create_time')
        })
        return context


class RegisterView(View):
    template_name = 'association/register.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class LoginView(View):
    template_name = 'association/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST['email'].strip()
        password = request.POST['password'].strip()
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)  # Todo 登入需防機器人
            return redirect('member')
        else:
            return render(request, self.template_name, {'messages': ['登入失敗']})


def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('member'))


class ForgotView(View):
    template_name = 'association/forgot.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST['email'].strip()
        try:
            user = User.objects.get(username=email)
        except ObjectDoesNotExist:
            return render(request, self.template_name, {'messages': ['您輸入的Email不存在']})

        send_mail(
            '台灣區塊鏈協會密碼通知',
            '您好，以下為您的密碼' + ' ' + user.myuser.password + ' 請妥善保管。',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return render(request, self.template_name, {'messages': ['密碼已寄送至您的信箱']})


class MemberView(generic.ListView):
    template_name = 'association/member.html'
    model = Message
    context_object_name = 'member_message_list'
    ordering = ['-create_time']

    def get_context_data(self, **kwargs):
        context = super(MemberView, self).get_context_data(**kwargs)
        context.update({
            'intro': Intro.objects.all()[1]
        })
        return context


class AddMessageView(View):
    template_name = 'association/member.html'

    def get(self, request, *args, **kwargs):
        return redirect('member')

    def post(self, request, *args, **kwargs):
        member_message = request.POST['member_message'].strip()

        if not 0 < len(member_message) <= 100:
            return render(request, self.template_name, {'messages': ['留言長度需介於1~100字元'],
                                                        'member_message': member_message,
                                                        'member_message_list': Message.objects.order_by('-create_time')})

        request.user.myuser.message_set.create(message=member_message)
        return redirect('member')


class ReplyMessageView(View):
    template_name = 'association/member.html'

    def get(self, request, *args, **kwargs):
        return redirect('member')

    def post(self, request, *args, **kwargs):
        id = request.POST['member_message_id']
        message = Message.objects.get(pk=id)
        reply = request.POST['reply']

        message.reply = reply
        message.status = True
        message.save()
        return redirect('member')


class MLoginView(View):
    template_name = 'association/m_login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('m_member')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST['email'].strip()
        password = request.POST['password'].strip()

        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('m_member')
        else:
            return render(request, self.template_name, {'messages': ['登入失敗']})


def Mlogout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('m_login'))


class MMemberView(View):
    template_name = 'association/m_member.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name, {'member_list': MyUser.objects.all()})


class AddMemberView(View):
    template_name = 'association/add_member.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST['email'].strip()
        password1 = request.POST['password1'].strip()
        password2 = request.POST['password2'].strip()
        name = request.POST['name'].strip()
        id_number = request.POST['id_number'].strip()
        phone = request.POST['phone'].strip()
        address = request.POST['address'].strip()

        messages = []
        if not re.match(email_re, email):
            messages.append('電子郵件格式不符')
        if User.objects.filter(username=email):
            messages.append('該電子郵件已存在')
        if not 8 <= len(password1) <= 20:
            messages.append('密碼長度為8~20')
        if password1 != password2:
            messages.append('密碼不一致')
        if id_number and len(id_number) != 10:
            messages.append('身分證格式不符')
        if phone and not re.match(phone_re, phone):
            messages.append('電話格式不符')
        if messages:
            return render(request, self.template_name, {'messages': messages,
                                                        'email': email,
                                                        'name': name,
                                                        'id_number': id_number,
                                                        'phone': phone,
                                                        'address': address})

        user = User.objects.create_user(username=email, password=password1)
        MyUser.objects.create(user=user, password=password1, name=name, id_number=id_number, phone=phone,
                              address=address, is_company=False)
        return redirect('m_member')


class EditMemberView(View):
    template_name = 'association/edit_member.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        pk = self.kwargs.get('pk')
        if pk:
            return render(request, self.template_name, {'member': MyUser.objects.get(pk=pk)})
        else:
            return redirect('m_member')

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        my_user = MyUser.objects.get(pk=id)
        name = request.POST['name'].strip()
        id_number = request.POST['id_number'].strip()
        phone = request.POST['phone'].strip()
        address = request.POST['address'].strip()
        # attendance = request.POST['attendance']

        messages = []
        if id_number and len(id_number) != 10:
            messages.append('身分證格式不符')
        if phone and not re.match(phone_re, phone):
            messages.append('電話格式不符')
        if messages:
            return render(request, self.template_name, {'messages': messages, 'member': my_user})

        my_user.name = name
        my_user.id_number = id_number
        my_user.phone = phone
        my_user.address = address
        # my_user.attendance = attendance
        my_user.save()
        return redirect('m_member')


class DeleteMemberView(View):
    template_name = 'association/m_member.html'

    def post(self, request, *args, **kwargs):
        id = request.POST['member_id']
        MyUser.objects.get(pk=id).user.delete()
        return redirect('m_member')


class MCompanyView(View):
    template_name = 'association/m_company.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name, {'company_list': Company.objects.all()})


class AddCompanyView(View):
    template_name = 'association/add_company.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST['email'].strip()
        password1 = request.POST['password1'].strip()
        password2 = request.POST['password2'].strip()
        name = request.POST['name'].strip()
        id_number = request.POST['id_number'].strip()
        phone = request.POST['phone'].strip()
        address = request.POST['address'].strip()
        category = request.POST['category'].strip()
        founder = request.POST['founder'].strip()
        intro = request.POST['intro']  # richText
        service = request.POST['service']  # richText
        milestone = request.POST['milestone']  # richText
        link = request.POST['link'].strip()
        group = request.POST['group']

        messages = []
        if not re.match(email_re, email):
            messages.append('電子郵件格式不符')
        if User.objects.filter(username=email):
            messages.append('該電子郵件已存在')
        if not 8 <= len(password1) <= 20:
            messages.append('密碼長度為8~20')
        if password1 != password2:
            messages.append('密碼不一致')
        if id_number and len(id_number) != 8:
            messages.append('統一編號格式不符')
        if phone and not re.match(phone_re, phone):
            messages.append('電話格式不符')
        if messages:
            return render(request, self.template_name, {'messages': messages,
                                                        'email': email,
                                                        'name': name,
                                                        'id_number': id_number,
                                                        'phone': phone,
                                                        'address': address,
                                                        'category': category,
                                                        'founder': founder,
                                                        'intro': intro,
                                                        'service': service,
                                                        'milestone': milestone,
                                                        'link': link,
                                                        'group': group})

        user = User.objects.create_user(username=email, password=password1)
        my_user = MyUser.objects.create(user=user, password=password1, name=name, id_number=id_number, phone=phone,
                                        address=address, is_company=True)
        Company.objects.create(my_user=my_user,
                               category=category,
                               founder=founder,
                               intro=intro,
                               service=service,
                               milestone=milestone,
                               link=link,
                               group=group)
        return redirect('m_company')


class EditCompanyView(View):
    template_name = 'association/edit_company.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        pk = self.kwargs.get('pk')
        if pk:
            return render(request, self.template_name, {'company': Company.objects.get(pk=pk)})
        else:
            return redirect('m_company')

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        company = Company.objects.get(pk=id)
        my_user = company.my_user
        name = request.POST['name'].strip()
        id_number = request.POST['id_number'].strip()
        phone = request.POST['phone'].strip()
        address = request.POST['address'].strip()
        attendance = request.POST['attendance']
        category = request.POST['category'].strip()
        founder = request.POST['founder'].strip()
        intro = request.POST['intro']  # richText
        service = request.POST['service']  # richText
        milestone = request.POST['milestone']  # richText
        link = request.POST['link'].strip()
        group = request.POST['group']

        messages = []
        if id_number and len(id_number) != 8:
            messages.append('統一編號格式不符')
        if phone and not re.match(phone_re, phone):
            messages.append('電話格式不符')
        if messages:
            return render(request, self.template_name, {'messages': messages, 'company': company})

        my_user.name = name
        my_user.id_number = id_number
        my_user.phone = phone
        my_user.address = address
        my_user.attendance = attendance
        my_user.save()
        company.category = category
        company.founder = founder
        company.intro = intro
        company.service = service
        company.milestone = milestone
        company.link = link
        company.group = group
        company.save()
        return redirect('m_company')


class DeleteCompanyView(View):
    template_name = 'association/m_company.html'

    def post(self, request, *args, **kwargs):
        id = request.POST['company_id']
        Company.objects.get(pk=id).my_user.user.delete()
        return redirect('m_company')


class MCourseView(View):
    template_name = 'association/m_course.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name, {'course_list': Course.objects.order_by('-create_time')})


class AddCourseView(View):
    template_name = 'association/add_course.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        image = request.FILES.get('image')
        course_name = request.POST['course_name']
        project_name = request.POST['project_name']
        permit_number = request.POST['permit_number']
        adviser = request.POST['adviser']
        organizer = request.POST['organizer']
        registration_date = request.POST['registration_date']
        venue = request.POST['venue']
        enrollment = request.POST['enrollment']
        training_cost = request.POST['training_cost']
        training_date = request.POST['training_date']
        training_time = request.POST['training_time']
        link = request.POST['link']
        content = request.POST['content']
        gender = request.POST['gender']
        education = request.POST['education']
        age = request.POST['age']
        military_service = request.POST['military_service']
        skill = request.POST['skill']
        condition = request.POST['condition']
        remark = request.POST['remark']

        Course.objects.create(image=image,
                              course_name=course_name,
                              project_name=project_name,
                              permit_number=permit_number,
                              adviser=adviser,
                              organizer=organizer,
                              registration_date=registration_date,
                              venue=venue,
                              enrollment=enrollment,
                              training_cost=training_cost,
                              training_date=training_date,
                              training_time=training_time,
                              link=link,
                              content=content,
                              gender=gender,
                              education=education,
                              age=age,
                              military_service=military_service,
                              skill=skill,
                              condition=condition,
                              remark=remark)
        return redirect('m_course')


class EditCourseView(View):
    template_name = 'association/edit_course.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        pk = self.kwargs.get('pk')
        if pk:
            return render(request, self.template_name, {'course': Course.objects.get(pk=pk)})
        else:
            return redirect('m_course')

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        course = Course.objects.get(pk=id)
        image = request.FILES.get('image')
        course_name = request.POST['course_name']
        project_name = request.POST['project_name']
        permit_number = request.POST['permit_number']
        adviser = request.POST['adviser']
        organizer = request.POST['organizer']
        registration_date = request.POST['registration_date']
        venue = request.POST['venue']
        enrollment = request.POST['enrollment']
        training_cost = request.POST['training_cost']
        training_date = request.POST['training_date']
        training_time = request.POST['training_time']
        link = request.POST['link']
        content = request.POST['content']
        gender = request.POST['gender']
        education = request.POST['education']
        age = request.POST['age']
        military_service = request.POST['military_service']
        skill = request.POST['skill']
        condition = request.POST['condition']
        remark = request.POST['remark']

        if image:
            course.image = image
        course.course_name = course_name
        course.project_name = project_name
        course.permit_number = permit_number
        course.adviser = adviser
        course.organizer = organizer
        course.registration_date = registration_date
        course.venue = venue
        course.enrollment = enrollment
        course.training_cost = training_cost
        course.training_date = training_date
        course.training_time = training_time
        course.link = link
        course.content = content
        course.gender = gender
        course.education = education
        course.age = age
        course.military_service = military_service
        course.skill = skill
        course.condition = condition
        course.remark = remark
        course.save()
        return redirect('m_course')


class DeleteCourseView(View):
    template_name = 'association/m_course.html'

    def post(self, request, *args, **kwargs):
        id = request.POST['course_id']
        Course.objects.get(pk=id).delete()
        return redirect('m_course')


class MNewsView(View):
    template_name = 'association/m_news.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name, {'news_list': News.objects.order_by('-create_time')})


class AddNewsView(View):
    template_name = 'association/add_news.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        form = NewsForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title'].strip()
            content = form.cleaned_data['content']
            image = form.cleaned_data['image']
            type = form.cleaned_data['type']

            form.save()
            # News.objects.create(title=title, content=content, image=image, type=type)
        return redirect('m_news')


class EditNewsView(View):
    template_name = 'association/edit_news.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        pk = self.kwargs.get('pk')
        news = News.objects.get(pk=pk)
        if pk:
            form = NewsForm(instance=news)
            return render(request, self.template_name, {'form': form, 'news': news})
        else:
            return redirect('m_news')

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        news = News.objects.get(pk=id)
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            title = form.cleaned_data['title'].strip()
            content = form.cleaned_data['content']
            image = form.cleaned_data['image']
            type = form.cleaned_data['type']

            form.save()
            # news.title = title
            # news.content = content
            # if image:
            #     news.image = image
            # news.type = type
            # news.save()
        return redirect('m_news')


class DeleteNewsView(View):
    template_name = 'association/m_news.html'

    def post(self, request, *args, **kwargs):
        id = request.POST['news_id']
        News.objects.get(pk=id).delete()
        return redirect('m_news')


class MResourceView(View):
    template_name = 'association/m_resource.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name, {'resource_list': Resource.objects.order_by('-create_time')})


class AddResourceView(View):
    template_name = 'association/add_resource.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        name = request.POST['name']
        category = request.POST['category']
        organization = request.POST['organization']
        period = request.POST['period']
        qualification = request.POST['qualification']
        link = request.POST['link']
        type = request.POST['type']

        Resource.objects.create(name=name, category=category, organization=organization, period=period,
                                qualification=qualification, link=link, type=type)
        return redirect('resource')


class EditResourceView(View):
    template_name = 'association/edit_resource.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        pk = self.kwargs.get('pk')
        if pk:
            return render(request, self.template_name, {'resource': Resource.objects.get(pk=pk)})
        else:
            return redirect('m_resource')

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        resource = Resource.objects.get(pk=id)
        name = request.POST['name']
        category = request.POST['category']
        organization = request.POST['organization']
        period = request.POST['period']
        qualification = request.POST['qualification']
        link = request.POST['link']
        type = request.POST['type']

        resource.name = name
        resource.category = category
        resource.organization = organization
        resource.period = period
        resource.qualification = qualification
        resource.link = link
        resource.type = type
        resource.save()
        return redirect('resource')


class DeleteResourceView(View):
    template_name = 'association/m_resource.html'

    def post(self, request, *args, **kwargs):
        id = request.POST['resource_id']
        Resource.objects.get(pk=id).delete()
        return redirect('m_resource')


class MIntroView(View):
    template_name = 'association/m_intro.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        intro = Intro.objects.all()[0]
        form = IntroForm(instance=intro)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        intro = Intro.objects.all()[0]
        form = IntroForm(request.POST, instance=intro)
        if form.is_valid():
            form.save()
        return redirect('m_intro')


class MBulletinView(View):
    template_name = 'association/m_bulletin.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        intro = Intro.objects.all()[1]
        form = IntroForm(instance=intro)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        intro = Intro.objects.all()[1]
        form = IntroForm(request.POST, instance=intro)
        if form.is_valid():
            form.save()
        return redirect('m_bulletin')


class MImgView(View):
    template_name = 'association/m_img.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        img_name = request.POST['img_name']  # e.g. 957.png
        img = request.FILES.get('img')
        img_path_out = 'static/img/' + img_name
        img_path_in = 'association/static/img/' + img_name

        if img:
            with open(img_path_out, 'wb') as f:
                for data in img.chunks():
                    f.write(data)
            with open(img_path_in, 'wb') as f:
                for data in img.chunks():
                    f.write(data)
        return redirect('m_img')


class MStaffView(View):
    template_name = 'association/m_staff.html'

    def get(self, request):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name, {'staff_list': MyUser.objects.filter(user__is_staff=True)})


class AddStaffView(View):
    template_name = 'association/add_staff.html'

    def get(self, request):
        if not request.user.is_staff:
            return redirect('m_login')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        name = request.POST['name']
        id_number = request.POST['id_number']
        phone = request.POST['phone']
        address = request.POST['address']

        messages = []
        if not re.match(email_re, email):
            messages.append('電子郵件格式不符')
        if User.objects.filter(username=email):
            messages.append('該電子郵件已存在')
        if not 8 <= len(password1) <= 20:
            messages.append('密碼長度為8~20')
        if password1 != password2:
            messages.append('密碼不一致')
        if id_number and len(id_number) != 10:
            messages.append('身分證格式不符')
        if phone and not re.match(phone_re, phone):
            messages.append('電話格式不符')
        if messages:
            return render(request, self.template_name, {'messages': messages,
                                                        'email': email,
                                                        'name': name,
                                                        'id_number': id_number,
                                                        'phone': phone,
                                                        'address': address})

        user = User.objects.create_user(username=email, password=password1, is_staff=True)
        MyUser.objects.create(user=user, password=password1, name=name, id_number=id_number, phone=phone,
                              address=address, is_company=False)
        return redirect('m_staff')


class EditStaffView(View):
    template_name = 'association/edit_staff.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('m_login')
        pk = self.kwargs.get('pk')
        if pk:
            return render(request, self.template_name, {'staff': MyUser.objects.get(pk=pk)})
        else:
            return redirect('m_staff')

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        my_user = MyUser.objects.get(pk=id)
        name = request.POST['name'].strip()
        id_number = request.POST['id_number'].strip()
        phone = request.POST['phone'].strip()
        address = request.POST['address'].strip()

        messages = []
        if id_number and len(id_number) != 10:
            messages.append('身分證格式不符')
        if phone and not re.match(phone_re, phone):
            messages.append('電話格式不符')
        if messages:
            return render(request, self.template_name, {'messages': messages, 'staff': my_user})

        my_user.name = name
        my_user.id_number = id_number
        my_user.phone = phone
        my_user.address = address
        my_user.save()
        return redirect('m_staff')


class DeleteStaffView(View):
    template_name = 'association/m_staff.html'

    def post(self, request, *args, **kwargs):
        id = request.POST['staff_id']
        MyUser.objects.get(pk=id).user.delete()
        return redirect('m_staff')
