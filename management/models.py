from django.db import models

class Room(models.Model):
    # ตัวเลือกสถานะห้องพัก
    STATUS_CHOICES = (
        ('available', 'ว่าง'),
        ('occupied', 'มีผู้เช่า'),
        ('booked', 'จองแล้ว'),
        ('maintenance', 'ซ่อมแซม'),
    )
    
    room_number = models.CharField(max_length=10, unique=True, verbose_name="เลขห้อง")
    floor = models.IntegerField(verbose_name="ชั้น")
    room_type = models.CharField(max_length=50, default="สตูดิโอ", verbose_name="ประเภทห้อง")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="ราคาเช่า/เดือน")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="สถานะ")

    def __str__(self):
        return f"ห้อง {self.room_number}"
class Tenant(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="ชื่อ")
    last_name = models.CharField(max_length=100, verbose_name="นามสกุล")
    phone = models.CharField(max_length=15, verbose_name="เบอร์โทรศัพท์")
    
    # เชื่อมผู้เช่าเข้ากับห้องพัก (1 ห้อง มีผู้เช่าหลัก 1 คน)
    # on_delete=models.SET_NULL หมายถึง ถ้าห้องถูกลบ ข้อมูลผู้เช่ายังอยู่แต่ค่าห้องจะเป็น Null (ว่างเปล่า)
    room = models.OneToOneField(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ห้องพักที่เช่า")
    
    move_in_date = models.DateField(verbose_name="วันที่ย้ายเข้า")
    is_active = models.BooleanField(default=True, verbose_name="ยังพักอยู่หรือไม่")

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ห้อง {self.room.room_number if self.room else 'ยังไม่มีห้อง'})"
    
    # ... (โค้ด Room และ Tenant เดิมอยู่ด้านบน) ...

class Invoice(models.Model):
    # เชื่อมกับตารางผู้เช่าและห้องพัก (ใช้ ForeignKey เพราะ 1 ห้อง/1 คน สามารถมีบิลได้หลายใบในหลายๆ เดือน)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="ผู้เช่า")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="ห้องพัก")
    
    month = models.CharField(max_length=50, verbose_name="บิลประจำเดือน (เช่น ม.ค. 2026)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ยอดชำระรวม")
    due_date = models.DateField(verbose_name="วันครบกำหนดชำระ")
    
    # สถานะของบิล
    STATUS_CHOICES = [
        ('pending', 'รอชำระ'),
        ('paid', 'ชำระแล้ว'),
        ('overdue', 'เกินกำหนด'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")

    def __str__(self):
        return f"บิลห้อง {self.room.room_number} ({self.month})"
    
class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังซ่อม'),
        ('completed', 'เสร็จสิ้น'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="ห้องพัก")
    title = models.CharField(max_length=200, verbose_name="หัวข้อแจ้งซ่อม") # เช่น แอร์ไม่เย็น, น้ำรั่ว
    description = models.TextField(blank=True, verbose_name="รายละเอียดเพิ่มเติม")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่แจ้ง")

    def __str__(self):
        return f"แจ้งซ่อม {self.room.room_number}: {self.title}"
# models.py (เพิ่มต่อท้าย)

class Contract(models.Model):
    CONTRACT_TYPES = (
        ('lease', 'สัญญาเช่า (เข้าพักเลย)'),
        ('booking', 'จองห้องพัก'),
    )
    STATUS_CHOICES = (
        ('active', 'กำลังเช่า (Active)'),
        ('expiring', 'ใกล้หมดอายุ'),
        ('pending', 'รอเซ็นสัญญา'),
    )

    contract_number = models.CharField(max_length=20, unique=True, verbose_name="เลขที่สัญญา")
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, verbose_name="ประเภทเอกสาร")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, verbose_name="ห้องพัก")
    tenant_name = models.CharField(max_length=150, verbose_name="ชื่อผู้เช่า/ผู้จอง")
    start_date = models.DateField(verbose_name="วันที่เริ่มต้น")
    end_date = models.DateField(null=True, blank=True, verbose_name="วันที่สิ้นสุด")
    deposit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="เงินมัดจำ/ประกัน")
    notes = models.TextField(blank=True, null=True, verbose_name="หมายเหตุเพิ่มเติม")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract_number} - {self.tenant_name}"
class Billing(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    billing_month = models.DateField()  # สำหรับรอบบิลประจำเดือน
    
    # ค่าเช่าและค่าบริการคงที่
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # ค่าน้ำ
    water_prev_meter = models.IntegerField(default=0)
    water_curr_meter = models.IntegerField(default=0)
    water_unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=20)
    
    # ค่าไฟ
    elec_prev_meter = models.IntegerField(default=0)
    elec_curr_meter = models.IntegerField(default=0)
    elec_unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=7)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('pending', 'ค้างชำระ'), ('paid', 'ชำระแล้ว')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        water_units = self.water_curr_meter - self.water_prev_meter
        elec_units = self.elec_curr_meter - self.elec_prev_meter
        
        water_total = water_units * self.water_unit_price
        elec_total = elec_units * self.elec_unit_price
        
        self.total_amount = self.rent_amount + self.service_fee + water_total + elec_total
        return self.total_amount