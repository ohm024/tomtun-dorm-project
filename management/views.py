from django.shortcuts import render
from .models import Room, Tenant  # 👈 นำเข้าตารางห้องพักและผู้เช่าที่เราสร้างไว้

def dashboard(request):
    # 1. สั่งให้ Django ไปนับข้อมูลในฐานข้อมูล (Database)
    total_rooms = Room.objects.count()  # นับจำนวนห้องทั้งหมด
    available_rooms = Room.objects.filter(status='available').count() # นับเฉพาะห้องที่สถานะ 'ว่าง'
    
    # 👉 เพิ่มบรรทัดนี้ครับ: นับห้องที่สถานะ 'ซ่อม' (ดูใน models.py ว่าคุณใช้คำว่าอะไร สมมติว่าใช้ 'maintenance')
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    
    # 👉 อัปเดตบรรทัดนี้ครับ: คำนวณห้องที่มีคนอยู่ (เอาห้องทั้งหมด - ห้องว่าง - ห้องซ่อม)
    occupied_rooms = total_rooms - available_rooms - maintenance_rooms 
    
    active_tenants = Tenant.objects.filter(is_active=True).count() # นับผู้เช่าที่ยังพักอยู่

    # 2. นำตัวเลขที่นับได้มาใส่ "กล่องพัสดุ" (Context) เพื่อเตรียมส่งไปให้หน้าเว็บ
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms, # 👈 อย่าลืมแพ็กใส่กล่องด้วย!
        'active_tenants': active_tenants,
    }

    # 3. ส่งหน้าเว็บ dashboard.html ไปแสดงผล พร้อมกับแนบ "กล่องพัสดุ (context)" ไปด้วย
    return render(request, 'dashboard.html', context)