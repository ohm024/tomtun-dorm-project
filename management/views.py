from django.shortcuts import render
from .models import Room  # สำคัญมาก: ต้องนำเข้า Model Room มาใช้งาน

def dashboard(request):
    # 1. สั่งให้ Django ไปนับข้อมูลในฐานข้อมูล
    total_rooms = Room.objects.count() # นับห้องทั้งหมด
    available_rooms = Room.objects.filter(status='available').count() # นับเฉพาะห้องว่าง
    occupied_rooms = Room.objects.filter(status='occupied').count() # นับเฉพาะห้องที่มีผู้เช่า
    maintenance_rooms = Room.objects.filter(status='maintenance').count() # นับเฉพาะห้องซ่อมแซม

    # 2. จับข้อมูลใส่กล่อง (Dictionary) เพื่อส่งไปที่หน้า HTML
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
    }
    
    # 3. ส่งกล่องข้อมูล (context) ไปพร้อมกับการ render หน้าเว็บ
    return render(request, 'dashboard.html', context)