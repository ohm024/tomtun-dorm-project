"""
URL configuration for tomtun_dorm project.
"""
from django.contrib import admin
from django.urls import path
from management import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),           # หน้าแรก (Dashboard)
    path('rooms/', views.rooms, name='rooms'),             # หน้าจัดการห้องพัก
    path('contracts/', views.contracts, name='contracts'), # หน้าการจองและสัญญา
    path('check-in-out/', views.check_in_out, name='check_in_out'), # หน้าเช็คอิน/เช็คเอาท์
    path('tenants/', views.tenants, name='tenants'),       # หน้าจัดการผู้เช่า
    
    # เพิ่มบรรทัดนี้สำหรับหน้าบิลค่าเช่าที่เราทำค้างไว้ครับ
    path('billing/', views.billing, name='billing'),       
]