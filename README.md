# panarint.com

เว็บไซต์ทางการของน้ำมังคุด ตรา พนารินทร์ (PANARIN) โดย บริษัท ทิพย์มงคล 555 จำกัด
เป็นเว็บ static (HTML/CSS) ไม่ต้อง build ก่อน deploy วางไฟล์ทั้งโฟลเดอร์บนโฮสต์ได้ทันที

## โครงสร้าง

- `tools/pages/*.html` เนื้อหาแต่ละหน้า พร้อม meta และ JSON-LD (home.html = หน้าแรก)
- `tools/partials/` header และ footer ที่ใช้ร่วมกันทุกหน้า
- `tools/data.json` ส่วนประกอบ 24 ชนิด, ใบรับรอง, กิจกรรมและข่าวสาร, ภาพลูกค้าและตัวแทน
- `tools/build_pages.py` สร้างไฟล์ HTML ทุกหน้า (ห้ามแก้ไฟล์ HTML ที่สร้างแล้วโดยตรง)
- `assets/img/site/` รูปจากเว็บเดิม thipmongkol555.com (แปลงเป็น WebP)
- `assets/css/site.css` สีและตัวอักษรตาม PANARIN Design System
- `robots.txt`, `sitemap.xml`, `llms.txt` สำหรับ SEO และ AEO

## แก้ไขเนื้อหา

```bash
python tools/build_pages.py
```

ดูตัวอย่างในเครื่อง: `python -m http.server 8765` แล้วเปิด http://localhost:8765
