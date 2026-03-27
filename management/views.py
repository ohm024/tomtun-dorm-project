from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import time

# รวบรวม Import Models ไว้ที่เดียวกัน
from .models import Room, Tenant, Invoice, MaintenanceRequest, Billing, Contract, CheckInOutLog

# ==========================================
# ระบบล็อกอิน / ล็อกเอาท์ (ไม่ต้องมี @login_required)
# ==========================================
def login_view(request):
    # ถ้าล็อกอินอยู่แล้ว ให้เด้งไปหน้าแดชบอร์ดเลย
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # เช็คว่า Username และ Password ตรงกับในฐานข้อมูลไหม
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user) # ทำการเข้าสู่ระบบ
            return redirect('dashboard') # สำเร็จแล้วไปหน้าแดชบอร์ด
        else:
            # รหัสผิด ให้ส่งข้อความแจ้งเตือนกลับไป
            messages.error(request, 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง')
            
    return render(request, 'login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request) # ล้างข้อมูลล็อกอิน
    return redirect('login') # เด้งกลับไปหน้า login

# ==========================================
# แดชบอร์ด
# ==========================================
@login_required(login_url='login')
def dashboard(request):
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

    today = datetime.now()
    month_names_th = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    
    bar_chart_labels = [] 
    bar_chart_data = []  
    
    dates_loop = []
    for i in range(11, -1, -1):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        
        label_th = month_names_th[m]
        bar_chart_labels.append(label_th)
        bar_chart_data.append(0) 
        dates_loop.append(datetime(y, m, 1))

    db_monthly_revenue = Invoice.objects.filter(
        status__in=['pending', 'paid']
    ).annotate(
        truncated_month=TruncMonth('due_date')
    ).values('truncated_month').annotate(
        total_rev=Sum('amount')
    ).order_by('truncated_month')

    for item in db_monthly_revenue:
        if item['truncated_month']:
            truncated_month_datetime = item['truncated_month']
            for idx, dt_iter in enumerate(dates_loop):
                if truncated_month_datetime.year == dt_iter.year and truncated_month_datetime.month == dt_iter.month:
                    bar_chart_data[idx] = float(item['total_rev'])
                    break 

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
        'bar_chart_labels': bar_chart_labels, 
        'bar_chart_data': bar_chart_data,    
    }
    return render(request, 'dashboard.html', context)

# ==========================================
# ระบบจัดการห้องพัก
# ==========================================
@login_required(login_url='login')
def rooms(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    all_rooms = Room.objects.all().order_by('room_number')

    if search_query:
        all_rooms = all_rooms.filter(room_number__icontains=search_query)

    if status_filter:
        all_rooms = all_rooms.filter(status=status_filter)
    
    context = {
        'rooms': all_rooms
    }
    return render(request, 'rooms.html', context)

@login_required(login_url='login')
def add_room(request):
    if request.method == 'POST':
        r_number = request.POST.get('room_number')
        r_type = request.POST.get('room_type')
        r_price = request.POST.get('price')
        r_status = request.POST.get('status')
        
        try:
            r_floor = int(''.join(filter(str.isdigit, r_number))[0])
        except:
            r_floor = 1

        Room.objects.create(
            room_number=r_number,
            floor=r_floor,
            room_type=r_type,
            price=r_price,
            status=r_status
        )
        return redirect('rooms')

    return render(request, 'add_room.html')

@login_required(login_url='login')
def edit_room(request, room_id):
    room = Room.objects.get(id=room_id)
    
    if request.method == 'POST':
        room.room_number = request.POST.get('room_number')
        room.room_type = request.POST.get('room_type')
        room.price = request.POST.get('price')
        room.status = request.POST.get('status')
        
        try:
            room.floor = int(''.join(filter(str.isdigit, room.room_number))[0])
        except:
            pass 
            
        room.save()
        return redirect('rooms')

    return render(request, 'edit_room.html', {'room': room})

@login_required(login_url='login')
def delete_room(request, room_id):
    room = Room.objects.get(id=room_id)
    room.delete()
    return redirect('rooms')

# ==========================================
# ระบบจัดการสัญญาเช่า
# ==========================================
@login_required(login_url='login')
def contracts(request):
    search_query = request.GET.get('search', '')
    all_contracts = Contract.objects.all().order_by('-created_at')
    
    if search_query:
        all_contracts = all_contracts.filter(
            Q(contract_number__icontains=search_query) | 
            Q(tenant_name__icontains=search_query) |
            Q(room__room_number__icontains=search_query) 
        )

    return render(request, 'contracts.html', {'contracts': all_contracts})

@login_required(login_url='login')
def add_contract(request):
    available_rooms = Room.objects.filter(status='available')
    
    if request.method == 'POST':
        c_type = request.POST.get('contract_type')
        prefix = "CT" if c_type == 'lease' else "BK"
        auto_contract_number = f"{prefix}-{int(time.time())}"

        new_contract = Contract.objects.create(
            contract_number=auto_contract_number,
            contract_type=c_type,
            room_id=request.POST.get('room_id'),
            tenant_name=request.POST.get('tenant_name'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            deposit=request.POST.get('deposit'),
            notes=request.POST.get('notes'),
            status='active' if c_type == 'lease' else 'pending'
        )

        room = Room.objects.get(id=request.POST.get('room_id'))
        room.status = 'occupied' if c_type == 'lease' else 'booked'
        room.save()

        return redirect('contracts')

    return render(request, 'add_contract.html', {'available_rooms': available_rooms})

@login_required(login_url='login')
def edit_contract(request, contract_id):
    contract = Contract.objects.get(id=contract_id)
    
    if request.method == 'POST':
        contract.tenant_name = request.POST.get('tenant_name')
        contract.deposit = request.POST.get('deposit')
        contract.status = request.POST.get('status')
        contract.notes = request.POST.get('notes')
        contract.save()
        return redirect('contracts') 
        
    return render(request, 'edit_contract.html', {'contract': contract})

# ==========================================
# ระบบเช็คอิน / เช็คเอาท์
# ==========================================
@login_required(login_url='login')
def check_in_out(request):
    logs = CheckInOutLog.objects.all().order_by('-transaction_date')
    return render(request, 'check_in_out.html', {'logs': logs})

@login_required(login_url='login')
def add_checkin(request):
    if request.method == 'POST':
        room = Room.objects.get(id=request.POST.get('room'))
        
        CheckInOutLog.objects.create(
            transaction_type='in',
            room=room,
            tenant_name=request.POST.get('tenant_name'), 
            transaction_date=request.POST.get('transaction_date'),
            water_meter=request.POST.get('water_meter', 0),
            electric_meter=request.POST.get('electric_meter', 0),
            key_received=request.POST.get('key_received') == 'on',
            notes=request.POST.get('notes', '')
        )
        room.status = 'occupied' 
        room.save()
        return redirect('check_in_out')

    rooms = Room.objects.exclude(status='occupied')
    return render(request, 'add_checkin.html', {'rooms': rooms})

@login_required(login_url='login')
def add_checkout(request):
    if request.method == 'POST':
        room = Room.objects.get(id=request.POST.get('room'))
        
        CheckInOutLog.objects.create(
            transaction_type='out',
            room=room,
            tenant_name=request.POST.get('tenant_name'),
            transaction_date=request.POST.get('transaction_date'),
            water_meter=request.POST.get('water_meter', 0),
            electric_meter=request.POST.get('electric_meter', 0),
            damage_fee=request.POST.get('damage_fee', 0),
            refund_deposit=request.POST.get('refund_deposit', 0),
            notes=request.POST.get('notes', '')
        )
        room.status = 'available'
        room.save()
        return redirect('check_in_out')

    rooms = Room.objects.filter(status='occupied')
    return render(request, 'add_checkout.html', {'rooms': rooms})

# ==========================================
# ระบบจัดการผู้เช่า
# ==========================================
@login_required(login_url='login')
def tenants(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    all_tenants = Tenant.objects.all().order_by('-id')
    
    if search_query:
        all_tenants = all_tenants.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(phone__icontains=search_query)
        )
    
    if status_filter == 'active':
        all_tenants = all_tenants.filter(is_active=True)
    elif status_filter == 'inactive':
        all_tenants = all_tenants.filter(is_active=False)

    return render(request, 'tenants.html', {
        'tenants': all_tenants,
        'search_query': search_query,
        'status_filter': status_filter
    })

@login_required(login_url='login')
def add_tenant(request):
    if request.method == 'POST':
        name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        room_id = request.POST.get('room')
        start_date = request.POST.get('start_date')

        room = Room.objects.get(id=room_id)
        tenant = Tenant.objects.create(
            first_name=name,
            phone=phone,
            room=room,
            move_in_date=start_date,
            is_active=True
        )
        
        room.status = 'occupied'
        room.save()
        return redirect('tenants') 

    available_rooms = Room.objects.exclude(status__icontains='มีผู้เช่า').exclude(status__icontains='occupied')
    return render(request, 'add_tenant.html', {'rooms': available_rooms})

@login_required(login_url='login')
def delete_tenant(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    room = tenant.room
    tenant.delete()
    
    if room:
        room.status = 'available'
        room.save()
        
    return redirect('tenants')

# ==========================================
# ระบบบิลค่าเช่า
# ==========================================
@login_required(login_url='login')
def billing(request):
    billings = Billing.objects.all().order_by('-created_at')
    
    total_unpaid = Billing.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    today = datetime.now()
    total_paid = Billing.objects.filter(status='paid', created_at__year=today.year, created_at__month=today.month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    pending_count = Billing.objects.filter(status='pending').count()

    context = {
        'billings': billings,
        'total_unpaid': total_unpaid,
        'total_paid': total_paid,
        'pending_count': pending_count,
    }
    return render(request, 'billing.html', context)

@login_required(login_url='login')
def add_bill(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = Room.objects.get(id=room_id)
        tenant = Tenant.objects.filter(room=room, is_active=True).first()
        
        rent = float(request.POST.get('rent_amount', 0))
        service = float(request.POST.get('service_fee', 0))
        
        w_prev = int(request.POST.get('water_prev', 0))
        w_curr = int(request.POST.get('water_curr', 0))
        water_total = (w_curr - w_prev) * 20
        
        e_prev = int(request.POST.get('elec_prev', 0))
        e_curr = int(request.POST.get('elec_curr', 0))
        elec_total = (e_curr - e_prev) * 7
        
        total = rent + service + water_total + elec_total
        
        month_str = request.POST.get('billing_month')
        billing_month_date = f"{month_str}-01" if month_str else None
        
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

    active_tenants = Tenant.objects.filter(is_active=True).exclude(room__isnull=True)
    return render(request, 'add_bill.html', {'active_tenants': active_tenants})

# ==========================================
# ระบบแจ้งซ่อม
# ==========================================
@login_required(login_url='login')
def maintenance(request):
    status_filter = request.GET.get('status', '')
    requests = MaintenanceRequest.objects.all().order_by('-created_at')
    
    if status_filter:
        requests = requests.filter(status=status_filter)
        
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

@login_required(login_url='login')
def add_maintenance(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = Room.objects.get(id=room_id)
        
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
        
    rooms = Room.objects.all()
    return render(request, 'add_maintenance.html', {'rooms': rooms})

@login_required(login_url='login')
def edit_maintenance(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    
    if request.method == 'POST':
        req.title = request.POST.get('title')
        req.description = request.POST.get('description', '')
        req.urgency = request.POST.get('urgency')
        req.status = request.POST.get('status') 
        
        appt_date = request.POST.get('appointment_date')
        req.appointment_date = appt_date if appt_date else None
        
        req.save()
        return redirect('maintenance') 
        
    return render(request, 'edit_maintenance.html', {'req': req})

@login_required(login_url='login')
def accept_maintenance(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    req.status = 'in_progress'
    req.save()
    return redirect('maintenance')

# ==========================================
# ระบบการตั้งค่า
# ==========================================
@login_required(login_url='login')
def settings_view(request):
    return render(request, 'settings.html')