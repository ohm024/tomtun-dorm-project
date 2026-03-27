from django.contrib import admin
from .models import Room,Tenant,MaintenanceRequest,Contract,Billing

# ปรับแต่งหน้าตาของตาราง Room ในหน้า Admin
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'floor', 'room_type', 'price', 'status') # คอลัมน์ที่จะโชว์
    list_filter = ('status', 'floor', 'room_type') # แถบตัวกรองด้านขวา
    search_fields = ('room_number',) # ช่องค้นหา

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    # เลือกคอลัมน์ที่จะให้โชว์เป็นตารางในหน้า Admin
    list_display = ('first_name', 'last_name', 'room', 'phone', 'is_active')
    
    # สร้างช่องค้นหาด้วย ชื่อ นามสกุล และเบอร์โทร
    search_fields = ('first_name', 'last_name', 'phone')
    
    # สร้างตัวกรองข้อมูลด้านขวามือ
    list_filter = ('is_active',)


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('room', 'title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('room__room_number', 'title')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'contract_type', 'room', 'tenant_name', 'start_date', 'status')
    list_filter = ('contract_type', 'status', 'start_date')
    search_fields = ('contract_number', 'tenant_name', 'room__room_number')

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    # กำหนดคอลัมน์ที่จะแสดงในหน้าตาราง
    list_display = ('room', 'tenant', 'billing_month', 'total_amount', 'status', 'due_date')
    
    # เพิ่มตัวกรองข้อมูลด้านขวามือ (กรองตามสถานะ หรือ เดือน)
    list_filter = ('status', 'billing_month')
    
    # เพิ่มช่องค้นหา (หาจากเลขห้อง หรือ ชื่อผู้เช่า)
    search_fields = ('room__room_number', 'tenant__first_name', 'tenant__last_name')
    
    # เรียงลำดับจากวันที่สร้างล่าสุดไปเก่าสุด
    ordering = ('-created_at',)