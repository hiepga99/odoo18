"""Policy: allowlist model, denylist field, read-only gate, trần limit.

Nguồn policy là DATA (ai.mcp.model — admin bật/tắt trên UI, xem models/mcp_model.py);
module khác vẫn mở rộng được bằng _inherit _get_policy().
LEGACY_PILOT_POLICY chỉ dùng cho bootstrap lần đầu (post_init_hook / migration).
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


# Allowlist/denylist pilot ban đầu — chỉ dùng để bootstrap record ai.mcp.model lần đầu.
LEGACY_PILOT_POLICY = {
    'res.partner':     {'fields_deny': []},
    'sale.order':      {'fields_deny': []},
    'crm.lead':        {'fields_deny': []},
    'stock.quant':     {'fields_deny': []},
    'hr.employee':     {'fields_deny': ['identification_id', 'bank_account_id']},
    'helpdesk.ticket': {'fields_deny': []},
    'account.move':    {'fields_deny': []},
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
