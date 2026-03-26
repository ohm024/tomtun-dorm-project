from django.shortcuts import render
from django.db.models import Sum
from .models import Room, Tenant, Invoice,MaintenanceRequest

def dashboard(request):
    # 1. นับข้อมูลห้องและผู้เช่า (ของเดิม)
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    occupied_rooms = total_rooms - available_rooms - maintenance_rooms
    active_tenants = Tenant.objects.filter(is_active=True).count()

    # คำนวณอัตราการเช่า (ของเดิม)
    if total_rooms > 0:
        occupancy_rate = (occupied_rooms / total_rooms) * 100
    else:
        occupancy_rate = 0

    # 2. คำนวณเรื่องเงินๆ ทองๆ (ของเดิม)
    expected_revenue = Invoice.objects.filter(status__in=['pending', 'paid']).aggregate(total=Sum('amount'))['total'] or 0
    overdue_amount = Invoice.objects.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0
    overdue_count = Invoice.objects.filter(status='overdue').count()

    # 🌟 3. ส่วนที่เพิ่มใหม่: ดึงข้อมูลมาทำรายการแจ้งเตือน
    # 3.1 ดึงรายการแจ้งซ่อมที่สถานะเป็น 'รอดำเนินการ' หรือ 'กำลังซ่อม' (เอามาแค่ 5 รายการล่าสุด)
    recent_maintenances = MaintenanceRequest.objects.filter(status__in=['pending', 'in_progress']).order_by('-created_at')[:5]
    
    # 3.2 ดึงบิลที่ 'เกินกำหนด' (เอามาโชว์ในลิสต์ 5 รายการ)
    overdue_invoices_list = Invoice.objects.filter(status='overdue').order_by('due_date')[:5]

    # 4. นำตัวเลขใส่กล่องพัสดุ
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'active_tenants': active_tenants,
        'occupancy_rate': occupancy_rate,
        'expected_revenue': expected_revenue,
        'overdue_amount': overdue_amount,
        'overdue_count': overdue_count,
        'recent_maintenances': recent_maintenances,       # 👈 ส่งรายการแจ้งซ่อมไปหน้าเว็บ
        'overdue_invoices_list': overdue_invoices_list,   # 👈 ส่งรายการบิลค้างชำระไปหน้าเว็บ
    }

    return render(request, 'dashboard.html', context)