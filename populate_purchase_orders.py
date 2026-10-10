# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'odoo18'])
registry = odoo.registry('odoo18')

SUPPLIERS = [
    {"name": "Công ty Cổ phần Phân phối Synnex FPT", "street": "Tòa nhà FPT, Phố Duy Tân, Cầu Giấy", "city": "Hà Nội", "phone": "02473006666", "email": "purchasing@synnexfpt.com.vn"},
    {"name": "Công ty Cổ phần Thế giới số (Digiworld - DGW)", "street": "195 Điện Biên Phủ, Phường 15, Bình Thạnh", "city": "TP. Hồ Chí Minh", "phone": "02839290059", "email": "supplier@digiworld.com.vn"},
    {"name": "Công ty TNHH Tin học Viễn Sơn", "street": "175 Nguyễn Thị Minh Khai, Quận 1", "city": "TP. Hồ Chí Minh", "phone": "02839250707", "email": "contact@vienson.vn"},
    {"name": "Công ty CP Dịch vụ Phân phối Tổng hợp Dầu khí (PSD)", "street": "Tòa nhà PetroVietnam, 1-5 Lê Duẩn, Quận 1", "city": "TP. Hồ Chí Minh", "phone": "02839115599", "email": "orders@psd.com.vn"},
    {"name": "Công ty TNHH Phân phối Công nghệ Vĩnh Xuân (SPC)", "street": "39 Trần Quốc Toản, Hoàn Kiếm", "city": "Hà Nội", "phone": "02439439121", "email": "kinhdoanh@spc.com.vn"},
    {"name": "Công ty CP Tập đoàn Sunhouse", "street": "Tầng 12, Tòa nhà Richy Tower, Mễ Trì Hạ, Nam Từ Liêm", "city": "Hà Nội", "phone": "02437366699", "email": "sales@sunhouse.com.vn"},
    {"name": "Công ty TNHH Philips Việt Nam", "street": "Tầng 20, Tòa nhà A&B Tower, 76A Lê Lai, Quận 1", "city": "TP. Hồ Chí Minh", "phone": "02838241515", "email": "b2b@philips.vn"},
    {"name": "Công ty TNHH Xiaomi Việt Nam", "street": "Tầng 18, Bitexco Financial Tower, Quận 1", "city": "TP. Hồ Chí Minh", "phone": "02839103888", "email": "distributor@xiaomi.com"},
    {"name": "Công ty TNHH Thương mại Quốc tế Thủy Linh (TLC)", "street": "33 Thái Hà, Đống Đa", "city": "Hà Nội", "phone": "02435371525", "email": "tlc@thuylinh.vn"},
    {"name": "Công ty Cổ phần Nội thất Hòa Phát", "street": "39 Nguyễn Đình Chiểu, Hai Bà Trưng", "city": "Hà Nội", "phone": "02462810666", "email": "banhang@hoaphat.com.vn"},
]

print("Starting purchase orders generation...")

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {'lang': 'vi_VN'})
    
    # 1. Tạo hoặc lấy nhà cung cấp
    Partner = env['res.partner']
    supplier_ids = []
    for s in SUPPLIERS:
        existing = Partner.search([('name', '=', s['name'])], limit=1)
        if existing:
            supplier_ids.append(existing.id)
        else:
            p = Partner.create({
                'name': s['name'],
                'is_company': True,
                'street': s['street'],
                'city': s['city'],
                'phone': s['phone'],
                'email': s['email'],
                'supplier_rank': 1,
            })
            supplier_ids.append(p.id)
    print(f"Suppliers ready: {len(supplier_ids)}")

    # 2. Lấy danh sách sản phẩm
    ProductProduct = env['product.product']
    products = ProductProduct.search([('default_code', 'like', 'SP%')])
    product_ids = [p.id for p in products]
    print(f"Products available for purchase: {len(product_ids)}")

    # 3. Tạo 80 Đơn mua hàng (Purchase Orders)
    PurchaseOrder = env['purchase.order']
    target_po_count = 80
    base_date = datetime(2026, 10, 7)
    
    states_distribution = ['purchase'] * 70 + ['draft'] * 20 + ['sent'] * 10
    
    for i in range(1, target_po_count + 1):
        partner_id = random.choice(supplier_ids)
        days_ago = random.randint(5, 360)
        po_date = base_date - timedelta(days=days_ago, hours=random.randint(1, 12))
        
        num_items = random.randint(2, 5)
        chosen_products = random.sample(product_ids, num_items)
        
        lines = []
        for pid in chosen_products:
            prod = ProductProduct.browse(pid)
            cost_price = prod.standard_price if prod.standard_price > 0 else (prod.list_price * 0.75)
            qty = random.choice([20, 30, 50, 80, 100])
            lines.append((0, 0, {
                'product_id': pid,
                'name': prod.name,
                'product_qty': qty,
                'price_unit': cost_price,
                'date_planned': po_date + timedelta(days=3),
            }))
            
        po = PurchaseOrder.create({
            'partner_id': partner_id,
            'date_order': po_date.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': 2, # Mitchell Admin
            'order_line': lines,
        })
        
        state_choice = random.choice(states_distribution)
        if state_choice == 'purchase':
            try:
                po.button_confirm()
            except Exception:
                pass
        elif state_choice == 'sent':
            po.write({'state': 'sent'})
            
        if i % 20 == 0:
            print(f"Created {i}/{target_po_count} purchase orders...")

    cr.commit()
    total_pos = PurchaseOrder.search_count([])
    print(f"Successfully generated purchase orders! Total PO in database: {total_pos}")
