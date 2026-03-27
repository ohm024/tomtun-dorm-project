from django.shortcuts import render
from django.db.models import Sum
from .models import Room, Tenant, Invoice,MaintenanceRequest,Billing
from django.db.models.functions import TruncMonth # 👈 ตัวจัดกลุ่มตามเดือน
from datetime import datetime, timedelta       # 👈 ตัวคำนวณวันเวลา
from django.shortcuts import redirect
from django.db.models import Q
from .models import Contract
import time # นำเข้า time เพื่อเอาไว้สุ่มเลขสัญญาชั่วคราว
from django.shortcuts import get_object_or_404

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
    # เปลี่ยนจาก 'q' เป็น 'search' ให้ตรงกับที่ตั้งไว้ใน HTML ครับ
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # ดึงข้อมูลห้องทั้งหมดมาเป็นฐานก่อน
    all_rooms = Room.objects.all().order_by('room_number')

    # ถ้ามีการพิมพ์ค้นหา ให้กรองเอาเฉพาะที่เลขห้องตรงกัน
    if search_query:
        all_rooms = all_rooms.filter(room_number__icontains=search_query)

    # ถ้ามีการเลือกสถานะ (status) ให้กรองตามสถานะนั้น
    if status_filter:
        all_rooms = all_rooms.filter(status=status_filter)
    
    context = {
        'rooms': all_rooms
    }
    return render(request, 'rooms.html', context)

def contracts(request):
    search_query = request.GET.get('search', '')
    
    # กรองข้อมูล
    all_contracts = Contract.objects.all().order_by('-created_at')
    
    if search_query:
        all_contracts = all_contracts.filter(
            Q(contract_number__icontains=search_query) | 
            Q(tenant_name__icontains=search_query) |
            Q(room__room_number__icontains=search_query) # ค้นหาด้วยเลขห้องก็ได้
        )

    return render(request, 'contracts.html', {'contracts': all_contracts})

def check_in_out(request):
    return render(request, 'check_in_out.html')

def tenants(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # ดึงข้อมูลผู้เช่าทั้งหมด
    all_tenants = Tenant.objects.all().order_by('-id')
    
    # ค้นหาด้วย ชื่อ หรือ เบอร์โทร
    if search_query:
        all_tenants = all_tenants.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(phone__icontains=search_query)
        )
    
    # กรองตามสถานะ (is_active)
    if status_filter == 'active':
        all_tenants = all_tenants.filter(is_active=True)
    elif status_filter == 'inactive':
        all_tenants = all_tenants.filter(is_active=False)

    return render(request, 'tenants.html', {
        'tenants': all_tenants,
        'search_query': search_query,
        'status_filter': status_filter
    })

# ฟังก์ชันสำหรับหน้าแสดงรายการบิลทั้งหมด (แก้ Error ที่เจอ)
def billing(request):
    # ดึงข้อมูลบิลทั้งหมดเรียงจากใหม่ไปเก่า
    billings = Billing.objects.all().order_by('-created_at')
    
    # คำนวณยอดรวมต่างๆ สำหรับแสดงใน Card ด้านบน
    total_unpaid = Billing.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # ยอดชำระแล้วเดือนนี้
    today = datetime.now()
    total_paid = Billing.objects.filter(status='paid', created_at__year=today.year, created_at__month=today.month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # นับจำนวนบิลที่รอชำระ
    pending_count = Billing.objects.filter(status='pending').count()

    context = {
        'billings': billings,
        'total_unpaid': total_unpaid,
        'total_paid': total_paid,
        'pending_count': pending_count,
    }
    return render(request, 'billing.html', context)

# ฟังก์ชันสำหรับบันทึกบิลใหม่และคำนวณเงิน
def add_bill(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = Room.objects.get(id=room_id)
        
        # ดึงข้อมูลผู้เช่าของห้องนั้น
        tenant = Tenant.objects.filter(room=room, is_active=True).first()
        
        # รับค่าเงินต่างๆ จาก Form
        rent = float(request.POST.get('rent_amount', 0))
        service = float(request.POST.get('service_fee', 0))
        
        # ค่าน้ำ (หน่วยละ 20)
        w_prev = int(request.POST.get('water_prev', 0))
        w_curr = int(request.POST.get('water_curr', 0))
        water_total = (w_curr - w_prev) * 20
        
        # ค่าไฟ (หน่วยละ 7)
        e_prev = int(request.POST.get('elec_prev', 0))
        e_curr = int(request.POST.get('elec_curr', 0))
        elec_total = (e_curr - e_prev) * 7
        
        total = rent + service + water_total + elec_total
        
        # แปลงเดือนจาก input type="month" (YYYY-MM) ให้เป็น DateField (YYYY-MM-01) เพื่อบันทึกลงฐานข้อมูล
        month_str = request.POST.get('billing_month')
        billing_month_date = f"{month_str}-01" if month_str else None
        
        # สร้างบิลใหม่
        Billing.objects.create(
            room=room,
            tenant=tenant,
            billing_month=billing_month_date,
            rent_amount=rent,
            service_fee=service,
            water_prev_meter=w_prev,
            water_curr_meter=w_curr,
            elec_prev_meter=e_prev,
            elec_curr_meter=e_curr,
            total_amount=total,
            due_date=request.POST.get('due_date'),
            status='pending'
        )
        return redirect('billing')

    # สำหรับหน้าเลือกห้อง เราจะดึงเฉพาะผู้เช่าที่ Active และมีห้องพักอยู่ เพื่อป้องกัน error ผูกบิลผิด
    active_tenants = Tenant.objects.filter(is_active=True).exclude(room__isnull=True)
    
    return render(request, 'add_bill.html', {'active_tenants': active_tenants})
def maintenance(request):
    # รับค่าจาก Dropdown กรองสถานะ
    status_filter = request.GET.get('status', '')
    
    # ดึงข้อมูลทั้งหมดเรียงจากใหม่ไปเก่า
    requests = MaintenanceRequest.objects.all().order_by('-created_at')
    
    if status_filter:
        requests = requests.filter(status=status_filter)
        
    # คำนวณยอดสรุปในการ์ดด้านบน
    pending_count = MaintenanceRequest.objects.filter(status='pending').count()
    in_progress_count = MaintenanceRequest.objects.filter(status='in_progress').count()
    waiting_count = MaintenanceRequest.objects.filter(status='waiting').count()
    
    today = datetime.now()
    completed_count = MaintenanceRequest.objects.filter(
        status='completed', 
        created_at__year=today.year, 
        created_at__month=today.month
    ).count()

    context = {
        'requests': requests,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'waiting_count': waiting_count,
        'completed_count': completed_count,
    }
    return render(request, 'maintenance.html', context)

def add_maintenance(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = Room.objects.get(id=room_id)
        
        # จัดการวันที่ ถ้าไม่ได้เลือกมาให้เป็น None
        appt_date = request.POST.get('appointment_date')
        if not appt_date:
            appt_date = None
            
        MaintenanceRequest.objects.create(
            room=room,
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            urgency=request.POST.get('urgency'),
            reporter=request.POST.get('reporter'),
            appointment_date=appt_date,
            status='pending'
        )
        return redirect('maintenance')
        
    # ดึงรายชื่อห้องทั้งหมดมาแสดงให้เลือก
    rooms = Room.objects.all()
    return render(request, 'add_maintenance.html', {'rooms': rooms})

# ฟังก์ชันนี้เอาไว้ให้กดปุ่ม "รับเรื่อง" แล้วเปลี่ยนสถานะทันที
def accept_maintenance(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    req.status = 'in_progress'
    req.save()
    return redirect('maintenance')
def settings_view(request):
    return render(request, 'settings.html')
def login_view(request):
    return render(request, 'login.html')
def add_tenant(request):
    if request.method == 'POST':
        # 1. รับค่าจากฟอร์ม (ต้องตรงกับ attribute 'name' ใน html)
        name = request.POST.get('full_name')
        id_card = request.POST.get('id_card')
        phone = request.POST.get('phone')
        email_line = request.POST.get('email_line')
        room_id = request.POST.get('room')
        start_date = request.POST.get('start_date')

        # 2. บันทึกข้อมูลผู้เช่า
        room = Room.objects.get(id=room_id)
        # แก้ไขตรงนี้: ใส่เฉพาะฟิลด์ที่ชัวร์ว่ามีใน Model
        tenant = Tenant.objects.create(
            first_name=name,
            phone=phone,
            room=room,
            move_in_date=start_date, # จาก Error ก่อนหน้า ฟิลด์นี้ต้องมี
            is_active=True
        )
        
        # 3. อัปเดตสถานะห้องพัก
        room.status = 'มีผู้เช่า' # หรือ 'occupied' ตามที่คุณตั้งค่าไว้
        room.save()

        return redirect('tenants') # บันทึกเสร็จให้กลับไปหน้าบันชีรายชื่อ

    # ส่งรายชื่อห้องที่ "ว่าง" ไปให้เลือกใน Dropdown
    available_rooms = Room.objects.exclude(status__icontains='มีผู้เช่า').exclude(status__icontains='occupied')
    return render(request, 'add_tenant.html', {'rooms': available_rooms})
def add_room(request):
    return render(request, 'add_room.html')
def add_room(request):
    if request.method == 'POST':
        # รับค่าที่ส่งมาจาก Form โดยอ้างอิงจาก 'name' ที่เราเพิ่งใส่ไปใน HTML
        r_number = request.POST.get('room_number')
        r_type = request.POST.get('room_type')
        r_price = request.POST.get('price')
        r_status = request.POST.get('status')
        
        # คาดเดา 'ชั้น' จากตัวเลขห้องตัวแรก (เพราะในฟอร์มไม่มีให้กรอก แต่ Model บังคับต้องมี)
        try:
            r_floor = int(''.join(filter(str.isdigit, r_number))[0])
        except:
            r_floor = 1

        # บันทึกข้อมูลลงฐานข้อมูล
        Room.objects.create(
            room_number=r_number,
            floor=r_floor,
            room_type=r_type,
            price=r_price,
            status=r_status
        )
        
        # บันทึกเสร็จให้เปลี่ยนหน้ากลับไปที่หน้ารายการห้องพัก
        return redirect('rooms')

    # ถ้าไม่ใช่ POST (คือผู้ใช้เพิ่งกดเข้ามาหน้านี้ครั้งแรก) ก็ให้แสดงหน้าฟอร์มปกติ
    return render(request, 'add_room.html')

def add_checkin(request):
    return render(request, 'add_checkin.html')

def add_checkout(request):
    return render(request, 'add_checkout.html')

def add_contract(request):
    # ดึงเฉพาะห้องที่สถานะ 'ว่าง' มาแสดงใน Dropdown
    available_rooms = Room.objects.filter(status='available')
    
    if request.method == 'POST':
        # สร้างเลขที่สัญญาแบบง่ายๆ อัตโนมัติ (เช่น CT-168... หรือ BK-168...)
        c_type = request.POST.get('contract_type')
        prefix = "CT" if c_type == 'lease' else "BK"
        auto_contract_number = f"{prefix}-{int(time.time())}"

        # บันทึกข้อมูลลงฐานข้อมูล
        new_contract = Contract.objects.create(
            contract_number=auto_contract_number,
            contract_type=c_type,
            room_id=request.POST.get('room_id'),
            tenant_name=request.POST.get('tenant_name'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None, # ถ้าไม่ได้กรอกให้เป็น None
            deposit=request.POST.get('deposit'),
            notes=request.POST.get('notes'),
            status='active' if c_type == 'lease' else 'pending'
        )

        # อัปเดตสถานะห้องพัก
        room = Room.objects.get(id=request.POST.get('room_id'))
        room.status = 'occupied' if c_type == 'lease' else 'booked'
        room.save()

        return redirect('contracts')

    return render(request, 'add_contract.html', {'available_rooms': available_rooms})

def edit_room(request, room_id):
    # ดึงข้อมูลห้องที่ต้องการแก้ไขจากฐานข้อมูล
    room = Room.objects.get(id=room_id)
    
    if request.method == 'POST':
        # รับค่าที่แก้ไขแล้วจากฟอร์ม
        room.room_number = request.POST.get('room_number')
        room.room_type = request.POST.get('room_type')
        room.price = request.POST.get('price')
        room.status = request.POST.get('status')
        
        # คาดเดา 'ชั้น' ใหม่เผื่อมีการเปลี่ยนเลขห้อง
        try:
            room.floor = int(''.join(filter(str.isdigit, room.room_number))[0])
        except:
            pass # ถ้าหาไม่ได้ก็ใช้ค่าเดิม
            
        # บันทึกการเปลี่ยนแปลง
        room.save()
        return redirect('rooms')

    # ถ้าเป็น GET ให้ส่งข้อมูลห้องเดิมไปแสดงในฟอร์ม
    return render(request, 'edit_room.html', {'room': room})

def delete_room(request, room_id):
    # ดึงข้อมูลห้องนั้นมา แล้วสั่งลบทิ้งเลย
    room = Room.objects.get(id=room_id)
    room.delete()
    return redirect('rooms')

from django.shortcuts import get_object_or_404, redirect
from .models import Tenant

def delete_tenant(request, pk):
    # ดึงข้อมูลผู้เช่าตาม ID (Primary Key)
    tenant = get_object_or_404(Tenant, pk=pk)
    
    # ดึงข้อมูลห้องพักของผู้เช่าคนนี้
    room = tenant.room
    
    # ลบข้อมูลผู้เช่าออกจากฐานข้อมูล
    tenant.delete()
    
    # เมื่อลบผู้เช่าแล้ว ให้อัปเดตสถานะห้องพักกลับเป็น "ว่าง"
    if room:
        room.status = 'ว่าง' # ตรวจสอบให้ตรงกับคำที่ใช้ในระบบของคุณ (เช่น 'ว่าง' หรือ 'Vacant')
        room.save()
        
    return redirect('tenants') # ลบเสร็จแล้วให้กลับไปที่หน้าแสดงรายชื่อผู้เช่า

def edit_contract(request, contract_id):
    # ดึงข้อมูลสัญญาเดิมมา
    contract = Contract.objects.get(id=contract_id)
    
    if request.method == 'POST':
        # รับค่าจากฟอร์มมาเขียนทับ
        contract.tenant_name = request.POST.get('tenant_name')
        contract.deposit = request.POST.get('deposit')
        contract.status = request.POST.get('status')
        contract.notes = request.POST.get('notes')
        contract.save() # บันทึกลง Database
        return redirect('contracts') # แก้เสร็จแล้วกลับไปหน้าหลัก
        
    return render(request, 'edit_contract.html', {'contract': contract})

# เพิ่มฟังก์ชันนี้ต่อท้ายสุดใน views.py
def edit_maintenance(request, pk):
    # ดึงข้อมูลรายการแจ้งซ่อมที่ต้องการแก้ไข
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    
    if request.method == 'POST':
        # รับค่าที่แก้ไขจากฟอร์ม
        req.title = request.POST.get('title')
        req.description = request.POST.get('description', '')
        req.urgency = request.POST.get('urgency')
        req.status = request.POST.get('status') # สิ่งสำคัญที่สุดคือการอัปเดตสถานะ
        
        appt_date = request.POST.get('appointment_date')
        req.appointment_date = appt_date if appt_date else None
        
        req.save()
        return redirect('maintenance') # เซฟเสร็จกลับไปหน้าตาราง
        
    return render(request, 'edit_maintenance.html', {'req': req})