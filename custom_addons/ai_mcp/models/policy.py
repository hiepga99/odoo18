"""Policy: allowlist model, denylist field, read-only gate, trần limit.

Nguồn policy là DATA (ai.mcp.model — admin bật/tắt trên UI, xem models/mcp_model.py);
module khác vẫn mở rộng được bằng _inherit _get_policy().
DEFAULT_POLICY bootstrap record cho model đã cài (post_init_hook lúc cài, migration khi nâng cấp).
"""
from odoo import models

DISPLAYABLE_TYPES = {
    'char', 'text', 'selection', 'date', 'datetime',
    'monetary', 'float', 'integer', 'boolean', 'many2one',
}

# Enforced by tools_generic registering only these ORM ops; do not add write tools.
READ_METHODS = frozenset({
    'search_read', 'read', 'search_count',
    'read_group', 'fields_get', 'name_search',
})


# Bộ model mặc định -> record ai.mcp.model (post_init_hook / migration gọi _bootstrap_default_policy).
# Chỉ tạo cho model đã cài; admin sửa/tắt trên UI sau đó. description viết cho LLM: dữ liệu gì, field nào quan trọng.
DEFAULT_POLICY = {
    'res.partner': {'fields_deny': [], 'description':
        "Contacts: customers, vendors, employees' partner records. Use for names, emails, phones, addresses."},
    'res.company': {'fields_deny': [], 'description':
        "Companies of this database (multi-company). Map company_id to a name/currency."},
    'product.template': {'fields_deny': ['standard_price'], 'description':
        "Product catalog (templates): name, default_code, list_price (sale price / giá bán), categ_id, uom_id, "
        "type, sale_ok, purchase_ok. Variants and stock are on product.product."},
    'product.product': {'fields_deny': ['standard_price'], 'description':
        "Product variants: default_code (internal reference), lst_price (sale price / giá bán), qty_available "
        "(on hand), virtual_available (forecast), product_tmpl_id. Use for 'giá', 'tồn kho' of one product."},
    'product.category': {'fields_deny': [], 'description':
        "Product categories (tree via parent_id)."},
    'product.pricelist': {'fields_deny': [], 'description':
        "Price lists (bảng giá) by customer/currency; rules are product.pricelist.item."},
    'product.pricelist.item': {'fields_deny': [], 'description':
        "Price list rules: pricelist_id, product_tmpl_id/product_id/categ_id, min_quantity, compute_price, "
        "fixed_price, percent_price, date_start/date_end."},
    'uom.uom': {'fields_deny': [], 'description': "Units of measure (đơn vị tính)."},
    'sale.order': {'fields_deny': [], 'description':
        "Sales quotations/orders: name, partner_id, date_order, state (draft=quotation, sale=confirmed), "
        "amount_untaxed, amount_total, user_id (salesperson), invoice_status. Lines: sale.order.line."},
    'sale.order.line': {'fields_deny': ['purchase_price', 'margin', 'margin_percent'], 'description':
        "Sales order lines: order_id, product_id, product_uom_qty, price_unit, discount, price_subtotal, "
        "qty_delivered, qty_invoiced. Use for 'customer X bought product Y', sold quantities, order details."},
    'purchase.order': {'fields_deny': [], 'description':
        "Purchase RFQ/orders: name, partner_id (vendor), date_order, date_approve, state, amount_total, "
        "user_id (buyer). Lines: purchase.order.line."},
    'purchase.order.line': {'fields_deny': [], 'description':
        "Purchase order lines: order_id, product_id, product_qty, price_unit, price_subtotal, qty_received, "
        "qty_invoiced, date_planned."},
    'account.move': {'fields_deny': [], 'description':
        "Invoices, bills, journal entries: move_type (out_invoice=customer invoice, out_refund=credit note, "
        "in_invoice=vendor bill, entry=journal entry), name, partner_id, invoice_date, invoice_date_due, "
        "amount_total, amount_residual (unpaid / còn nợ), payment_state, state (posted=validated)."},
    'account.move.line': {'fields_deny': [], 'description':
        "Invoice lines and journal items: move_id, partner_id, product_id, quantity, price_unit, price_subtotal, "
        "account_id, debit, credit, balance, date. Filter display_type='product' for invoice lines."},
    'account.payment': {'fields_deny': [], 'description':
        "Customer/vendor payments: partner_id, amount, date, payment_type (inbound/outbound), state, journal_id."},
    'stock.quant': {'fields_deny': [], 'description':
        "Stock on hand per product/location/lot: product_id, location_id, quantity, reserved_quantity, lot_id. "
        "Filter location_id.usage='internal' for real warehouse stock."},
    'stock.picking': {'fields_deny': [], 'description':
        "Transfers: receipts, deliveries, internal moves. picking_type_id, partner_id, origin (source document), "
        "state, scheduled_date, date_done. Lines: stock.move."},
    'stock.move': {'fields_deny': [], 'description':
        "Stock moves: picking_id, product_id, product_uom_qty (demand), quantity (done), location_id, "
        "location_dest_id, state, date."},
    'stock.lot': {'fields_deny': [], 'description':
        "Lots / serial numbers: name, product_id, expiration_date, product_qty."},
    'stock.warehouse': {'fields_deny': [], 'description': "Warehouses: name, code, lot_stock_id."},
    'stock.location': {'fields_deny': [], 'description':
        "Stock locations: complete_name, usage (internal, customer, supplier, inventory), warehouse_id."},
    'hr.employee': {'fields_deny': ['identification_id', 'bank_account_id', 'passport_id', 'ssnid', 'sinid', 'visa_no', 'permit_no', 'private_email', 'private_phone', 'private_street', 'private_street2', 'private_city', 'private_zip', 'private_state_id', 'private_country_id', 'private_car_plate', 'emergency_contact', 'emergency_phone', 'birthday', 'place_of_birth', 'country_of_birth', 'gender', 'marital', 'spouse_complete_name', 'spouse_birthdate', 'children', 'km_home_work', 'distance_home_work'], 'description':
        "Employees: name, job_title, department_id, parent_id (manager), work_email, work_phone, company_id. "
        "Private/ID/bank/family data is hidden."},
    'hr.department': {'fields_deny': [], 'description': "Departments: name, manager_id, parent_id."},
    'hr.job': {'fields_deny': [], 'description': "Job positions: name, department_id, no_of_employee."},
    'calendar.event': {'fields_deny': [], 'description':
        "Calendar meetings: name, start, stop, partner_ids (attendees), user_id, location."},
    'crm.lead': {'fields_deny': [], 'description':
        "CRM leads/opportunities: name, partner_id, stage_id, expected_revenue, probability, user_id."},
    'helpdesk.ticket': {'fields_deny': [], 'description':
        "Helpdesk tickets: name, partner_id, stage_id, priority, user_id, team_id."},
}


class PolicyError(Exception):
    pass


class AiMcpPolicy(models.AbstractModel):
    _name = 'ai.mcp.policy'
    _description = 'AI MCP Policy'

    def _get_policy(self):
        # Policy = data (admin cấu hình UI). Trả dict mới mỗi lần — override được phép mutate.
        return {m: dict(v) for m, v in self.env['ai.mcp.model']._policy_map().items()}

    def _available_models(self):
        """Model user này thực sự truy vấn được: có trong policy + đã cài + có ACL đọc."""
        return sorted(m for m in self._get_policy()
                      if m in self.env and self.env[m].has_access('read'))

    def check_model(self, model):
        # Đồng bộ với list_models: thiếu ACL đọc cũng chặn tại đây — mọi tool đi chung một cổng
        policy = self._get_policy()
        if model not in policy or model not in self.env or not self.env[model].has_access('read'):
            raise PolicyError(
                "Model '%s' không nằm trong phạm vi được phép. Model khả dụng: %s"
                % (model, ', '.join(self._available_models())))

    def check_query(self, model, domain=None, order=None):
        """Denylist + field-ACL áp cho cả domain (kể cả any/all lồng nhau, dotted path)
        và order — chặn dò giá trị field bị ẩn qua điều kiện lọc/sắp xếp."""
        def check_path(mod, path):
            cur = mod
            parts = path.split('.')
            for i, part in enumerate(parts):
                base = part.split(':')[0]
                if not self._field_allowed(cur, base):
                    raise PolicyError(
                        "Field '%s' không được phép dùng trong domain/order trên model '%s'."
                        % (path, mod))
                field = self.env[cur]._fields.get(base) if cur in self.env else None
                if field is None:
                    return None   # field không tồn tại -> để ORM tự báo lỗi tham số
                if i < len(parts) - 1:
                    if not field.comodel_name:
                        return None
                    cur = field.comodel_name
            return field

        def walk(mod, dom):
            for leaf in (dom or []):
                if isinstance(leaf, (list, tuple)) and len(leaf) == 3                         and isinstance(leaf[0], str):
                    field = check_path(mod, leaf[0])
                    if leaf[1] in ('any', 'not any') and field is not None                             and field.comodel_name and isinstance(leaf[2], (list, tuple)):
                        walk(field.comodel_name, leaf[2])

        walk(model, domain)
        for term in (order or '').split(','):
            name = term.strip().split(' ')[0]
            if name:
                check_path(model, name)

    def clamp_limit(self, limit):
        try:
            limit = int(limit) if limit else 20
        except (TypeError, ValueError):
            limit = 20
        return max(1, min(limit, 200))

    def filter_fields(self, model, fields):
        deny = set(self._get_policy().get(model, {}).get('fields_deny', []))
        Model = self.env[model]
        if fields:
            return [
                name for name in fields
                if name not in deny
                and (name not in Model._fields or Model._fields[name].is_accessible(self.env))
            ]
        # default chỉ lấy field stored — compute non-stored có thể đọc chéo model
        # (vd res.partner.days_sales_outstanding đọc account.move) gây AccessError cho user ít quyền
        meta = Model.fields_get(attributes=['type', 'store'])
        return [
            name for name, attrs in meta.items()
            if attrs['type'] in DISPLAYABLE_TYPES
            and attrs.get('store')
            and name not in deny
            and (name not in Model._fields or Model._fields[name].is_accessible(self.env))
        ]

    def _field_allowed(self, model, name):
        """True if a groupby/aggregate field spec is allowed (deny + ACL)."""
        if name == '__count' or name.startswith('__'):
            return True
        base = name.split(':')[0]
        deny = set(self._get_policy().get(model, {}).get('fields_deny', []))
        if base in deny:
            return False
        Model = self.env[model]
        if base in Model._fields and not Model._fields[base].is_accessible(self.env):
            return False
        return True

    def filter_groupby_fields(self, model, fields):
        """Strip denylist / inaccessible fields from groupby or aggregates specs."""
        return [name for name in (fields or []) if self._field_allowed(model, name)]
