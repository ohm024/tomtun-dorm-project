from django.shortcuts import render
# from .models import Room # ถ้ายังไม่มีโมเดล คอมเมนต์ไว้ก่อนได้ครับ

def dashboard(request):
    # --- ข้อมูลจำลอง (Mock Data) อิงตาม Figma เอามาจัด UI ---
    context = {
        'total_rooms': 120,            # เปลี่ยนเป็น 120 ห้อง
        'available_rooms': 20,         # ว่าง 20
        'occupied_rooms': 95,          # มีผู้เช่า 95
        'maintenance_rooms': 5,        # ซ่อม 5
        'revenue': "540,000",          # รายได้
        'overdue': "15,000",           # ค้างชำระ
        'growth_percentage': 85        # อัตราการเข้าพัก
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