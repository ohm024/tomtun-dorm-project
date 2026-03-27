# 🏢 ระบบจัดการห้องพักรายเดือน 

ระบบสำหรับบริหารจัดการหอพักและอพาร์ตเมนต์แบบครบวงจร ครอบคลุมตั้งแต่การจัดการข้อมูลห้องพัก การทำสัญญาเช่า การจดมิเตอร์น้ำ-ไฟ และการออกใบแจ้งหนี้ประจำเดือน

---

## 👥 2.1 ทีมงานและบทบาทหน้าที่ (Team Members & Roles)
1. **นายอัครพนธ์ อรุณ** รหัสนักศึกษา: 68030319
   - **Role:** Project Manager & Backend Developer
   - **หน้าที่:** เขียนโค้ดฝั่งBackend ,และเขียนเอกสาร README
2. **นายณัฐพล พงษ์จินดาวัฒน์** รหัสนักศึกษา: 68030358
   - **Role:** UX/UI Designer & Frontend Developer
   - **หน้าที่:** ออกแบบ UI Figma หน้าadmin ,เขียนโค้ดฝั่งFrontend
3. **นายภูบดินทร์ สัญโญ** รหัสนักศึกษา: 68030404
   - **Role:** UX/UI Designer
   - **หน้าที่:** ออกแบบ UI Figma หน้าUser ,ออกแบบ ER Diagram
4. **นางสาวสุธาสินี  มีอ้น** 68030434
   - **Role:** UX/UI Designer
   - **หน้าที่:**   ออกแบบ UI Figma หน้าadmin
5. **อากิล พรมชู** 68030449
   - **Role:** UX/UI Designer
   - **หน้าที่:** ออกแบบ UI Figma หน้าUser

---

## 📑 2.2 เอกสารความต้องการของระบบ (SRS)


---

## 🎨 2.3 ผลงานการออกแบบ (System Design)

### 1. System Architecture
<img width="752" height="666" alt="image" src="https://github.com/user-attachments/assets/2ac965ea-5d63-4760-91ea-ee74699dacf3" />


### 2. Use Case Diagram
<img width="980" height="725" alt="image" src="https://github.com/user-attachments/assets/cab2a3db-a8d7-48b4-80f6-06fc149cf299" />

- **Actors:** Admin (ผู้ดูแลระบบ), Tenant (ผู้เช่า)

---

### 3. Activity Diagram
<img width="276" height="744" alt="image" src="https://github.com/user-attachments/assets/edfc929e-0143-4059-ba5d-430b39253141" />
<img width="648" height="665" alt="image" src="https://github.com/user-attachments/assets/4b6a918d-279b-4ce7-811c-28cbcbfc9a3f" />
<img width="411" height="513" alt="image" src="https://github.com/user-attachments/assets/4dbc7424-63c3-4493-a7db-571ea111997b" />

ส่วนของการออกบิล

<img width="518" height="1079" alt="image" src="https://github.com/user-attachments/assets/bd42d53e-ceae-40c5-991d-d977ba82da48" />


### 4. ER Diagram
<img width="1313" height="1064" alt="image" src="https://github.com/user-attachments/assets/cfa04892-fb22-43e4-bbff-ef95352a24f7" />

---

### 6. UX/UI Design
- **Figma Design:https://www.figma.com/design/UvzengjynBO3aH7dTtoyo8/%E0%B8%AB%E0%B8%AD%E0%B8%9E%E0%B8%B1%E0%B8%81-%E0%B8%95%E0%B9%89%E0%B8%A1%E0%B8%95%E0%B8%B8%E0%B9%8B%E0%B8%99?node-id=0-1&t=ZWFoPFXkpDJBXWUY-1
<img width="691" height="797" alt="image" src="https://github.com/user-attachments/assets/6d28e810-d28d-4781-abac-b17e1aa681ea" />
<img width="761" height="766" alt="image" src="https://github.com/user-attachments/assets/d8eb8f87-9417-4682-9883-ae3a60fd75b2" />
<img width="383" height="768" alt="image" src="https://github.com/user-attachments/assets/516f5f62-e43f-4a3f-880f-24735431b418" />

---

### 7. API End-Points (ระบบเส้นทาง URL ภายในระบบ)
| HTTP Method | URL Path (End-Point) | หน้าที่การทำงาน (Description) |
| :--- | :--- | :--- |
| `GET` | `/` | แสดงหน้า Dashboard สรุปข้อมูลและกราฟ |
| `GET` | `/rooms/` | แสดงรายการห้องพักทั้งหมดและค้นหา |
| `GET` / `POST` | `/rooms/add/` | แสดงฟอร์มและบันทึกข้อมูลห้องพักใหม่ |
| `GET` / `POST` | `/rooms/edit/<id>/` | แก้ไขข้อมูลห้องพัก |
| `POST` | `/rooms/delete/<id>/` | ลบข้อมูลห้องพัก |
| `GET` | `/tenants/` | แสดงรายการผู้เช่าทั้งหมด |
| `GET` / `POST` | `/tenants/add/` | เพิ่มผู้เช่าใหม่และอัปเดตสถานะห้องเป็น "มีผู้เช่า" |
| `POST` | `/tenants/delete/<id>/` | ลบผู้เช่าและคืนสถานะห้องให้กลับเป็น "ว่าง" |
| `GET` | `/billing/` | แสดงตารางรายการบิลใบแจ้งหนี้ทั้งหมด |
| `GET` / `POST` | `/billing/add/` | รับเลขมิเตอร์ คำนวณค่าน้ำ-ไฟ และบันทึกบิล |
| `GET` / `POST` | `/contracts/add/` | บันทึกข้อมูลสัญญาและเจนเลขสัญญา (CT/BK) |

---

## 🛠️ 2.4 Tech Stack & Tools

- **Frontend:** HTML5, CSS3, Bootstrap 5 / TailwindCSS, JavaScript
- **Backend:** Python (Django Framework)
- **Database:** SQLite 
- **Design:** Figma, Draw.io (สำหรับ Diagrams)
- **Project Management:** GitHub, Git

---
