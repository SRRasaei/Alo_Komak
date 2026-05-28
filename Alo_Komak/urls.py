from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # احراز هویت
    path('login/',  auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # صفحات اصلی
    path('', views.quick_search, name='quick_search'),
    path('create-request/<int:customer_id>/', views.create_service_request, name='create_service_request'),
    path('change-status/<int:request_id>/',  views.change_service_status,   name='change_service_status'),

    # جدید: مودال و بارگذاری پاره‌ای (partial)
    path('get-request-modal/<int:customer_id>/', views.request_modal, name='request_modal'),
    path('recent-requests/<int:customer_id>/', views.recent_requests_partial, name='recent_requests_partial'),

    path('add-vehicle-modal/<int:customer_id>/', views.add_vehicle_modal, name='add_vehicle_modal'),
    path('vehicle-list/<int:customer_id>/', views.vehicle_list_partial, name='vehicle_list_partial'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('print-request/<int:request_id>/', views.print_service_request, name='print_service_request'),

]