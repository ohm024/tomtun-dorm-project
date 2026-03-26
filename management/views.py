from django.shortcuts import render
from django.db.models import Sum
from .models import Room, Tenant, Invoice,MaintenanceRequest
from django.db.models.functions import TruncMonth # 👈 ตัวจัดกลุ่มตามเดือน
from datetime import datetime, timedelta       # 👈 ตัวคำนวณวันเวลา

# management/views.py

def dashboard(request):
    # ==========================================
    # ส่วนเดิม (นับสถิติห้อง/ผู้เช่า/เงินรวม/แจ้งเตือน) - เก็บไว้ครบ
    # ==========================================
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    occupied_rooms = total_rooms - available_rooms - maintenance_rooms
    active_tenants = Tenant.objects.filter(is_active=True).count()

    if total_rooms > 0:
        occupancy_rate = (occupied_rooms / total_rooms) * 100
    else:
        occupancy_rate = 0

    expected_revenue = Invoice.objects.filter(status__in=['pending', 'paid']).aggregate(total=Sum('amount'))['total'] or 0
    overdue_amount = Invoice.objects.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0
    overdue_count = Invoice.objects.filter(status='overdue').count()
    
    recent_maintenances = MaintenanceRequest.objects.filter(status__in=['pending', 'in_progress']).order_by('-created_at')[:5]
    overdue_invoices_list = Invoice.objects.filter(status='overdue').order_by('due_date')[:5]

    # ==========================================
    # 🌟 ส่วนที่เพิ่มใหม่: เตรียมข้อมูลกราฟรายได้ย้อนหลัง 12 เดือน 🌟
    # ==========================================
    
    # 1. เตรียมรายชื่อ 12 เดือนล่าสุดในภาษาไทย (Past -> Present)
    # เพื่อให้แน่ใจว่าได้ 12 แท่งแม้บางเดือนไม่มีรายได้
    today = datetime.now()
    month_names_th = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    
    bar_chart_labels = [] # เก็บ "ม.ค.", "ก.พ."
    bar_chart_data = []   # เก็บยอดเงิน 0
    
    # ย้อนกลับไป 11 เดือนที่แล้วจนถึงเดือนนี้
    dates_loop = []
    for i in range(11, -1, -1):
        # คำนวณวันเดือนย้อนหลัง
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        
        # จัดรูปแบบป้าย (เช่น "ม.ค.")
        label_th = month_names_th[m]
        bar_chart_labels.append(label_th)
        bar_chart_data.append(0) # ใส่ 0 ไว้ก่อน
        
        # เก็บวันที่เริ่มต้นเดือนนั้นๆ ไว้เทียบกับ database
        dates_loop.append(datetime(y, m, 1))

    # 2. ไปดึงข้อมูลรายได้จากตาราง Invoice มาจัดกลุ่มตามเดือน
    # โดยอ้างอิงจาก field 'due_date' (ถือว่าเป็นวันจ่ายเงินของเดือนนั้นๆ)
    db_monthly_revenue = Invoice.objects.filter(
        status__in=['pending', 'paid'] # เอาเฉพาะบิลที่จ่ายแล้วหรือรอชำระ
    ).annotate(
        # สั่งให้จัดกลุ่มตามเดือนของ due_date
        truncated_month=TruncMonth('due_date')
    ).values('truncated_month').annotate(
        # บวกเลขยอดเงินรวมของเดือนนั้น
        total_rev=Sum('amount')
    ).order_by('truncated_month')

    # 3. นำข้อมูลจาก database มายัดใส่โครงที่เราเตรียมไว้
    for item in db_monthly_revenue:
        # DB บางตัวอาจไม่มี date จัดกลุ่ม
        if item['truncated_month']:
            truncated_month_datetime = item['truncated_month']
            # เทียบปีเทียบเดือนกับที่เราวนลูปเตรียมไว้
            for idx, dt_iter in enumerate(dates_loop):
                if truncated_month_datetime.year == dt_iter.year and truncated_month_datetime.month == dt_iter.month:
                    # ถ้าเจอเดือนที่ตรงกัน ให้ใส่ยอดเงินจริงลงไป (แปลง Decimal เป็น float เพื่อให้ JavaScript อ่านได้)
                    bar_chart_data[idx] = float(item['total_rev'])
                    break # เจอแล้วหยุดวนลูปด้านในไปอันถัดไป

    # ==========================================
    # ส่งข้อมูลทั้งหมดไปหน้าเว็บ
    # ==========================================
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
        'recent_maintenances': recent_maintenances,
        'overdue_invoices_list': overdue_invoices_list,
        # 🌟 2 ตัวแปรใหม่สำหรับกราฟแท่ง
        'bar_chart_labels': bar_chart_labels, # ["ม.ค.", "ก.พ.", ...]
        'bar_chart_data': bar_chart_data,     # [0, 4500, 0, ...]
    }
    
    return render(request, 'dashboard.html', context)

def rooms(request):
    return render(request, 'rooms.html')

def contracts(request):
    return render(request, 'contracts.html')

def check_in_out(request):
    return render(request, 'check_in_out.html')

def tenants(request):
    return render(request, 'tenants.html')

# 👇 เพิ่มฟังก์ชันนี้สำหรับหน้า "บิลค่าเช่า" ครับ
def billing(request):
    return render(request, 'billing.html')