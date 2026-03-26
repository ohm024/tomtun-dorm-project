from django.shortcuts import render
from django.db.models import Sum
from .models import Room, Tenant, Invoice

def dashboard(request):
    # 1. นับข้อมูลห้องและผู้เช่า
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    occupied_rooms = total_rooms - available_rooms - maintenance_rooms
    active_tenants = Tenant.objects.filter(is_active=True).count()

    # 🌟 ส่วนที่เพิ่มใหม่: คำนวณอัตราการเช่า (Occupancy Rate)
    if total_rooms > 0:
        occupancy_rate = (occupied_rooms / total_rooms) * 100
    else:
        occupancy_rate = 0  # ดักไว้เผื่อระบบยังไม่มีห้องเลย จะได้ไม่ error หารด้วยศูนย์

    # 2. คำนวณเรื่องเงินๆ ทองๆ
    expected_revenue = Invoice.objects.filter(status__in=['pending', 'paid']).aggregate(total=Sum('amount'))['total'] or 0
    overdue_amount = Invoice.objects.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0
    overdue_count = Invoice.objects.filter(status='overdue').count()

    # 3. นำตัวเลขใส่กล่องพัสดุ
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'active_tenants': active_tenants,
        'occupancy_rate': occupancy_rate,      # 👈 แพ็กเปอร์เซ็นต์อัตราการเช่าใส่กล่อง
        'expected_revenue': expected_revenue,
        'overdue_amount': overdue_amount,
        'overdue_count': overdue_count,
    }

    return render(request, 'dashboard.html', context)