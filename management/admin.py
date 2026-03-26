from django.contrib import admin
from .models import Room

# ปรับแต่งหน้าตาของตาราง Room ในหน้า Admin
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'floor', 'room_type', 'price', 'status') # คอลัมน์ที่จะโชว์
    list_filter = ('status', 'floor', 'room_type') # แถบตัวกรองด้านขวา
    search_fields = ('room_number',) # ช่องค้นหา