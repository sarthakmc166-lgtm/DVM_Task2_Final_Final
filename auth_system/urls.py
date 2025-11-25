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
from django.contrib.auth import views as auth_views
from admin_ui import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
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
    path('ticket/confirm/', ticket_views.ticket_confirmation, name='confirm_ticket'),
    path('line/', admin_views.line, name='line'),
    path('admin-menu/',admin_views.admin_menu,name='admin-menu'),
    path('add-line/',admin_views.add_line,name='add-line'),
    path('delete-line/<int:line_id>/', admin_views.delete_line, name='delete-line'),
    path('toggle-line/<int:line_id>/',admin_views.toggle_line,name='toggle-line'),
    path('metrostation/',admin_views.metrostation,name='metrostation'),
    path('add-metrostation/',admin_views.add_metrostation,name='add-metrostation'),
    path("stationconnections/", admin_views.stationconnections, name="stationconnections"),
    path("add-connection/", admin_views.add_connection, name="add-connection"),
    path('delete-metrostation/<int:station_id>/', admin_views.delete_metrostation, name='delete-metrostation'),
    path("view-tickets/", admin_views.view_tickets, name="view-tickets"),
    path("system-toggles/", admin_views.system_toggle, name="system-toggle"),
    path("toggle-system/<str:field>/", admin_views.toggle_system, name="toggle-system"),
    path("footfall/", admin_views.footfall, name="footfall"),
    path("add-footfall/", admin_views.add_footfall, name="add-footfall"),
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

