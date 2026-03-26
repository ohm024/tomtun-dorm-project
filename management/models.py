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