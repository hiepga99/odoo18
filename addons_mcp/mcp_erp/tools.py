# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from .odoo_client import OdooClient

odoo = OdooClient()

# ==============================================================================
# DANH SÁCH 12 CÔNG CỤ MCP CHUYÊN BIỆT KẾT NỐI ODOO 18 ERP
# ==============================================================================

# Tool 1: Tra cứu thông tin chi tiết sản phẩm
def get_product_info(keyword_or_code: str) -> Dict[str, Any]:
    """Tra cứu chi tiết sản phẩm: tên, giá niêm yết, giá vốn, mã vạch, danh mục"""
    try:
        domain = ['|', ('name', 'ilike', keyword_or_code), ('default_code', 'ilike', keyword_or_code)]
        fields = ['id', 'name', 'list_price', 'standard_price', 'default_code', 'barcode', 'categ_id', 'qty_available']
        records = odoo.execute_kw('product.template', 'search_read', [domain], {'fields': fields, 'limit': 3})
        if records:
            p = records[0]
            pname = p['name']
            if isinstance(pname, dict):
                pname = pname.get('vi_VN') or pname.get('en_US') or str(pname)
            return {
                "status": "success",
                "product_id": p['id'],
                "name": pname,
                "code": p.get('default_code') or "",
                "list_price": p.get('list_price', 0),
                "cost_price": p.get('standard_price', 0),
                "barcode": p.get('barcode') or "",
                "category": p['categ_id'][1] if p.get('categ_id') else "",
                "stock_available": p.get('qty_available', 0)
            }
        return {"status": "not_found", "message": f"Không tìm thấy sản phẩm khớp với '{keyword_or_code}'"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 2: Kiểm tra tồn kho khả dụng
def check_inventory_stock(product_name: str) -> Dict[str, Any]:
    """Kiểm tra số lượng tồn kho khả dụng thực tế của sản phẩm"""
    try:
        domain = [('name', 'ilike', product_name)]
        fields = ['id', 'name', 'qty_available', 'virtual_available']
        records = odoo.execute_kw('product.product', 'search_read', [domain], {'fields': fields, 'limit': 3})
        if records:
            p = records[0]
            pname = p['name']
            if isinstance(pname, dict):
                pname = pname.get('vi_VN') or pname.get('en_US') or str(pname)
            return {
                "status": "success",
                "product": pname,
                "qty_on_hand": p.get('qty_available', 0),
                "qty_forecasted": p.get('virtual_available', 0),
                "warehouse": "Kho chính Hà Nội",
                "unit": "Chiếc"
            }
        return {"status": "not_found", "message": f"Không tìm thấy hàng trong kho cho '{product_name}'"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 3: Tìm kiếm khách hàng / đối tác
def search_customers(query: str, limit: int = 5) -> Dict[str, Any]:
    """Tìm kiếm khách hàng theo tên công ty, số điện thoại hoặc email"""
    try:
        domain = ['|', '|', ('name', 'ilike', query), ('phone', 'ilike', query), ('email', 'ilike', query)]
        fields = ['id', 'name', 'phone', 'email', 'street', 'city', 'is_company']
        records = odoo.execute_kw('res.partner', 'search_read', [domain], {'fields': fields, 'limit': limit})
        return {
            "status": "success",
            "total_found": len(records),
            "customers": records
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 4: Tra cứu công nợ khách hàng
def get_customer_debt(customer_name: str) -> Dict[str, Any]:
    """Tra cứu tổng công nợ phải thu của khách hàng"""
    try:
        partner_records = odoo.execute_kw('res.partner', 'search_read', [[('name', 'ilike', customer_name)]], {'fields': ['id', 'name', 'total_due', 'credit'], 'limit': 1})
        if partner_records:
            p = partner_records[0]
            debt = p.get('credit', 0) or p.get('total_due', 0)
            return {
                "status": "success",
                "customer": p['name'],
                "total_debt": debt,
                "currency": "VNĐ",
                "payment_term": "30 ngày",
                "status_debt": "Trong hạn mức tín dụng" if debt < 100000000 else "Cần theo dõi"
            }
        return {"status": "not_found", "message": f"Không tìm thấy khách hàng '{customer_name}'"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 5: Tra cứu đơn bán hàng
def search_sale_orders(customer_name: str = "", state: str = "all", limit: int = 5) -> Dict[str, Any]:
    """Tra cứu danh sách đơn hàng theo khách hàng hoặc trạng thái đơn"""
    try:
        domain = []
        if customer_name:
            domain.append(('partner_id.name', 'ilike', customer_name))
        if state and state != "all":
            domain.append(('state', '=', state))
        fields = ['name', 'date_order', 'partner_id', 'amount_total', 'state']
        orders = odoo.execute_kw('sale.order', 'search_read', [domain], {'fields': fields, 'limit': limit})
        res_orders = []
        for o in orders:
            res_orders.append({
                "code": o['name'],
                "date": o['date_order'],
                "customer": o['partner_id'][1] if o.get('partner_id') else "",
                "total_amount": o['amount_total'],
                "state": o['state']
            })
        return {"status": "success", "count": len(res_orders), "orders": res_orders}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 6: Xem chi tiết các dòng trong đơn hàng
def get_order_detail(order_code: str) -> Dict[str, Any]:
    """Xem danh sách sản phẩm, số lượng, giá và tổng tiền của một đơn hàng"""
    try:
        orders = odoo.execute_kw('sale.order', 'search_read', [[('name', '=', order_code)]], {'fields': ['id', 'name', 'partner_id', 'amount_total', 'order_line', 'state'], 'limit': 1})
        if not orders:
            return {"status": "not_found", "message": f"Không tìm thấy đơn hàng {order_code}"}
        order = orders[0]
        line_ids = order.get('order_line', [])
        lines = odoo.execute_kw('sale.order.line', 'read', [line_ids], {'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit', 'price_subtotal']})
        return {
            "status": "success",
            "order_code": order['name'],
            "customer": order['partner_id'][1] if order.get('partner_id') else "",
            "total_amount": order['amount_total'],
            "state": order['state'],
            "items": [
                {
                    "product": l['name'],
                    "quantity": l['product_uom_qty'],
                    "unit_price": l['price_unit'],
                    "subtotal": l['price_subtotal']
                } for l in lines
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 7: Tạo báo giá mới (Quotation)
def create_quotation(customer_name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Tạo báo giá mới (nháp) trên Odoo ERP cho khách hàng"""
    try:
        # Tìm khách hàng
        partners = odoo.execute_kw('res.partner', 'search', [[('name', 'ilike', customer_name)]], {'limit': 1})
        if not partners:
            return {"status": "error", "message": f"Không tìm thấy khách hàng '{customer_name}'"}
        partner_id = partners[0]
        
        # Chuẩn bị dòng sản phẩm
        order_lines = []
        for it in items:
            pname = it.get('product_name', '')
            qty = it.get('quantity', 1)
            prods = odoo.execute_kw('product.product', 'search_read', [[('name', 'ilike', pname)]], {'fields': ['id', 'name', 'list_price'], 'limit': 1})
            if prods:
                prod = prods[0]
                order_lines.append((0, 0, {
                    'product_id': prod['id'],
                    'product_uom_qty': qty,
                    'price_unit': prod['list_price']
                }))
        
        if not order_lines:
            return {"status": "error", "message": "Không tìm thấy sản phẩm nào hợp lệ để tạo báo giá."}

        order_id = odoo.execute_kw('sale.order', 'create', [{
            'partner_id': partner_id,
            'order_line': order_lines
        }])
        new_order = odoo.execute_kw('sale.order', 'read', [[order_id]], {'fields': ['name', 'amount_total', 'state']})[0]
        return {
            "status": "success",
            "order_id": order_id,
            "order_code": new_order['name'],
            "total_amount": new_order['amount_total'],
            "state": new_order['state'],
            "message": f"Đã tạo thành công báo giá {new_order['name']} cho khách hàng {customer_name}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 8: Xác nhận đơn bán hàng (Confirm Sale Order)
def confirm_sale_order(order_code: str) -> Dict[str, Any]:
    """Xác nhận đơn báo giá thành Đơn bán hàng chính thức và kích hoạt xuất kho"""
    try:
        order_ids = odoo.execute_kw('sale.order', 'search', [[('name', '=', order_code)]], {'limit': 1})
        if not order_ids:
            return {"status": "not_found", "message": f"Không tìm thấy đơn hàng {order_code}"}
        res = odoo.execute_kw('sale.order', 'action_confirm', [order_ids])
        return {"status": "success", "order_code": order_code, "action": "confirmed", "message": f"Đã xác nhận đơn hàng {order_code} thành công!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 9: Báo cáo phân tích doanh thu
def get_revenue_analytics(period: str = "all") -> Dict[str, Any]:
    """Phân tích tổng doanh thu, số đơn hàng đã chốt và giá trị trung bình đơn"""
    try:
        orders = odoo.execute_kw('sale.order', 'search_read', [[('state', 'in', ['sale', 'done'])]], {'fields': ['amount_total']})
        total_rev = sum(o['amount_total'] for o in orders)
        count = len(orders)
        avg = (total_rev / count) if count > 0 else 0
        return {
            "status": "success",
            "period": period,
            "total_revenue": total_rev,
            "confirmed_orders_count": count,
            "average_order_value": round(avg, 2),
            "currency": "VNĐ"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 10: Tra cứu đơn mua hàng từ nhà cung cấp
def search_purchase_orders(supplier_name: str = "", limit: int = 5) -> Dict[str, Any]:
    """Tra cứu các đơn đặt mua hàng từ nhà phân phối chính hãng"""
    try:
        domain = []
        if supplier_name:
            domain.append(('partner_id.name', 'ilike', supplier_name))
        fields = ['name', 'partner_id', 'date_order', 'amount_total', 'state']
        pos = odoo.execute_kw('purchase.order', 'search_read', [domain], {'fields': fields, 'limit': limit})
        res = []
        for p in pos:
            res.append({
                "po_code": p['name'],
                "supplier": p['partner_id'][1] if p.get('partner_id') else "",
                "date": p['date_order'],
                "total_amount": p['amount_total'],
                "state": p['state']
            })
        return {"status": "success", "count": len(res), "purchase_orders": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 11: Tra cứu tình trạng xuất kho và phiếu giao hàng
def get_delivery_status(state: str = "all", limit: int = 5) -> Dict[str, Any]:
    """Tra cứu danh sách các lệnh giao hàng xuất kho cho khách"""
    try:
        domain = [('picking_type_id.code', '=', 'outgoing')]
        if state and state != "all":
            domain.append(('state', '=', state))
        fields = ['name', 'partner_id', 'scheduled_date', 'state', 'origin']
        pickings = odoo.execute_kw('stock.picking', 'search_read', [domain], {'fields': fields, 'limit': limit})
        res = []
        for p in pickings:
            res.append({
                "delivery_code": p['name'],
                "source_doc": p.get('origin') or "",
                "customer": p['partner_id'][1] if p.get('partner_id') else "",
                "state": p['state']
            })
        return {"status": "success", "count": len(res), "delivery_orders": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 12: Thống kê Top sản phẩm bán chạy nhất
def get_top_selling_products(limit: int = 5) -> Dict[str, Any]:
    """Thống kê top sản phẩm có doanh số bán cao nhất trong hệ thống"""
    try:
        lines = odoo.execute_kw('sale.order.line', 'search_read', [[('state', 'in', ['sale', 'done'])]], {'fields': ['product_id', 'product_uom_qty', 'price_subtotal'], 'limit': 100})
        prod_agg = {}
        for l in lines:
            if not l.get('product_id'):
                continue
            pid, pname = l['product_id']
            if pid not in prod_agg:
                prod_agg[pid] = {'name': pname, 'qty': 0, 'revenue': 0}
            prod_agg[pid]['qty'] += l.get('product_uom_qty', 0)
            prod_agg[pid]['revenue'] += l.get('price_subtotal', 0)
        sorted_prods = sorted(prod_agg.values(), key=lambda x: x['revenue'], reverse=True)[:limit]
        return {
            "status": "success",
            "top_products": sorted_prods
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Bảng map 12 Tools để MCP Server hoặc Agent gọi theo tên
MCP_TOOL_MAP = {
    "get_product_info": get_product_info,
    "check_inventory_stock": check_inventory_stock,
    "search_customers": search_customers,
    "get_customer_debt": get_customer_debt,
    "search_sale_orders": search_sale_orders,
    "get_order_detail": get_order_detail,
    "create_quotation": create_quotation,
    "confirm_sale_order": confirm_sale_order,
    "get_revenue_analytics": get_revenue_analytics,
    "search_purchase_orders": search_purchase_orders,
    "get_delivery_status": get_delivery_status,
    "get_top_selling_products": get_top_selling_products,
}
