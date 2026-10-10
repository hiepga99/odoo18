# -*- coding: utf-8 -*-
import random
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'odoo18'])
registry = odoo.registry('odoo18')

print("Starting warehouse inventory boost and picking validation...")

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {'lang': 'vi_VN'})
    
    StockQuant = env['stock.quant']
    StockLocation = env['stock.location']
    ProductProduct = env['product.product']
    StockPicking = env['stock.picking']
    
    stock_loc = StockLocation.search([('usage', '=', 'internal')], limit=1)
    
    # 1. Bơm tồn kho cơ bản dồi dào cho 160 sản phẩm (mỗi sản phẩm từ 200 đến 600 chiếc)
    all_products = ProductProduct.search([])
    print(f"Boosting inventory for {len(all_products)} products...")
    for prod in all_products:
        try:
            qty_add = random.randint(200, 600)
            StockQuant._update_available_quantity(prod, stock_loc, qty_add)
        except Exception:
            pass
    print("Initial stock boosted!")

    # 2. Hoàn thành (validate) 50 Phiếu nhập kho (Receipts)
    incoming_pickings = StockPicking.search([
        ('picking_type_id.code', '=', 'incoming'),
        ('state', 'in', ['assigned', 'confirmed'])
    ], limit=50)
    print(f"Validating {len(incoming_pickings)} incoming receipts...")
    for p in incoming_pickings:
        try:
            for move in p.move_ids:
                move.quantity = move.product_uom_qty
            p.button_validate()
        except Exception:
            pass
    print("Incoming receipts validated!")

    # 3. Giao hàng cho các đơn bán hàng: Kiểm tra khả dụng & Validate 200 đơn giao hàng
    outgoing_pickings = StockPicking.search([
        ('picking_type_id.code', '=', 'outgoing'),
        ('state', 'in', ['confirmed', 'assigned'])
    ])
    print(f"Assigning stock to {len(outgoing_pickings)} delivery orders...")
    try:
        outgoing_pickings.action_assign()
    except Exception:
        pass
        
    deliveries_to_validate = StockPicking.search([
        ('picking_type_id.code', '=', 'outgoing'),
        ('state', '=', 'assigned')
    ], limit=200)
    print(f"Validating {len(deliveries_to_validate)} deliveries to 'done'...")
    for p in deliveries_to_validate:
        try:
            for move in p.move_ids:
                move.quantity = move.product_uom_qty
            p.button_validate()
        except Exception:
            pass

    cr.commit()
    print("Done! Warehouse operations committed successfully.")
