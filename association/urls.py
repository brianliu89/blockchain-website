from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'association'
urlpatterns = [
    path('tbda957admin/', admin.site.urls),  # django內建後台
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', views.IndexView.as_view(), name='index'),
    path('news_list/', views.NewsListView.as_view(), name='news_list'),
    path('news_article/<int:pk>/', views.NewsArticleView.as_view(), name='news_article'),
    path('intro/', views.IntroView.as_view(), name='intro'),
    path('course/', views.CourseView.as_view(), name='course'),
    path('course_detail/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('add_course_message/', views.AddCourseMessageView.as_view(), name='add_course_message'),
    path('reply_course_message/', views.ReplyCourseMessageView.as_view(), name='reply_course_message'),
    path('company/', views.CompanyView.as_view(), name='company'),
    path('company_detail/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('resource/', views.ResourceView.as_view(), name='resource'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgot/', views.ForgotView.as_view(), name='forgot'),
    path('member/', views.MemberView.as_view(), name='member'),
    path('add_message/', views.AddMessageView.as_view(), name='add_message'),
    path('reply_message/', views.ReplyMessageView.as_view(), name='reply_message'),
    path('m_login/', views.MLoginView.as_view(), name='m_login'),
    path('m_logout/', views.Mlogout, name='m_logout'),
    path('m_member/', views.MMemberView.as_view(), name='m_member'),
    path('add_member/', views.AddMemberView.as_view(), name='add_member'),
    path('edit_member/<int:pk>/', views.EditMemberView.as_view(), name='edit_member'),
    path('delete_member/', views.DeleteMemberView.as_view(), name='delete_member'),
    path('m_company/', views.MCompanyView.as_view(), name='m_company'),
    path('add_company/', views.AddCompanyView.as_view(), name='add_company'),
    path('edit_company/<int:pk>/', views.EditCompanyView.as_view(), name='edit_company'),
    path('delete_company/', views.DeleteCompanyView.as_view(), name='delete_company'),
    path('m_course/', views.MCourseView.as_view(), name='m_course'),
    path('add_course/', views.AddCourseView.as_view(), name='add_course'),
    path('edit_course/<int:pk>/', views.EditCourseView.as_view(), name='edit_course'),
    path('delete_course/', views.DeleteCourseView.as_view(), name='delete_course'),
    path('m_news/', views.MNewsView.as_view(), name='m_news'),
    path('add_news/', views.AddNewsView.as_view(), name='add_news'),
    path('edit_news/<int:pk>/', views.EditNewsView.as_view(), name='edit_news'),
    path('delete_news/', views.DeleteNewsView.as_view(), name='delete_news'),
    path('m_resource/', views.MResourceView.as_view(), name='m_resource'),
    path('add_resource/', views.AddResourceView.as_view(), name='add_resource'),
    path('edit_resource/<int:pk>/', views.EditResourceView.as_view(), name='edit_resource'),
    path('delete_resource/', views.DeleteResourceView.as_view(), name='delete_resource'),
    path('m_intro/', views.MIntroView.as_view(), name='m_intro'),
    path('m_bulletin/', views.MBulletinView.as_view(), name='m_bulletin'),
    path('m_img/', views.MImgView.as_view(), name='m_img'),
    path('m_staff/', views.MStaffView.as_view(), name='m_staff'),
    path('add_staff/', views.AddStaffView.as_view(), name='add_staff'),
    path('edit_staff/<int:pk>/', views.EditStaffView.as_view(), name='edit_staff'),
    path('delete_staff/', views.DeleteStaffView.as_view(), name='delete_staff'),  # 以上為後台系統
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += i18n_patterns(
#     path('admin/', admin.site.urls),  # django內建後台
#     path('', views.IndexView.as_view(), name='index'),
#     path('news_list/', views.NewsListView.as_view(), name='news_list'),
#     path('news_article/<int:pk>/', views.NewsArticleView.as_view(), name='news_article'),
#     path('intro/', views.IntroView.as_view(), name='intro'),
#     path('course/', views.CourseView.as_view(), name='course'),
#     path('course_detail/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
#     path('add_course_message/', views.AddCourseMessageView.as_view(), name='add_course_message'),
#     path('register/', views.RegisterView.as_view(), name='register'),
#     path('login/', views.LoginView.as_view(), name='login'),
#     path('logout/', views.logout, name='logout'),
#     path('forgot/', views.ForgotView.as_view(), name='forgot'),
#     path('member/', views.MemberView.as_view(), name='member'),
#     path('member_detail/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
#     path('resource/', views.ResourceView.as_view(), name='resource'),  # 以上為前台系統
# )
