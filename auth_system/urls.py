"""
URL configuration for auth_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views
from ticket import views as ticket_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('ticket/book/', ticket_views.book_ticket, name='book_ticket'),
    path('menu/', ticket_views.menu, name='menu'),
    path('menu/add/', ticket_views.add_balance, name='add_balance'),
    path('menu/scan/', ticket_views.ticket_scanner, name='scan'),
    path('menu/view/', ticket_views.view_ticket, name='view'),
    path('down/', ticket_views.down, name='down'),
    path('accounts/', include('allauth.urls')), # all urls needed by allauth ex: /accounts/login/ it doesnt clash with normal user login
    path('', views.landing_page_view, name='landing'),
    path('otp-verification/<str:ticket_id>/', ticket_views.otp_verification, name='otp_verification'),
    path('staff-login/', views.staff_login, name='staff_login'),
    path('post-login/', views.post_login, name = 'pre-menu'),
    path('offline-ticket/', ticket_views.offline_ticket_booking, name='offline-ticket'),
    path('offline-confirmation/', ticket_views.offline_confirmation, name='offline-confirmation'),

]
