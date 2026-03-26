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