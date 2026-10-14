from odoo import api, fields, models, tools


class AiMcpModel(models.Model):
    """Model được mở cho MCP + field bị ẩn. FK cascade tới ir.model: gỡ module -> record tự mất (không stale).

    Không đặt flag trực tiếp trên ir.model vì (1) base.group_user không có quyền đọc ir.model,
    (2) core khoá write trên ir.model.fields của base field. Bảng riêng có ACL read cho user thường.
    """
    _name = 'ai.mcp.model'
    _description = 'AI MCP Exposed Model'
    _order = 'model_name'
    _rec_name = 'model_name'

    model_id = fields.Many2one('ir.model', required=True, ondelete='cascade', index=True)
    model_name = fields.Char(related='model_id.model', store=True, index=True)
    active = fields.Boolean(default=True, help='Tắt = AI không truy vấn được model này')
    description = fields.Char(help='Mô tả cho LLM: dữ liệu gì, dùng khi nào (khác với _description cho người)')
    deny_field_ids = fields.Many2many(
        'ir.model.fields', 'ai_mcp_model_deny_field_rel', 'mcp_model_id', 'field_id',
        string='Hidden fields', domain="[('model_id', '=', model_id)]",
        help='Field bị ẩn khỏi AI dù user có quyền đọc (PII, lương, ...)')
    deny_field_names = fields.Json(compute='_compute_deny_field_names', store=True)

    _sql_constraints = [
        ('model_uniq', 'unique(model_id)', 'Model already configured for MCP.'),
    ]

    @api.depends('deny_field_ids')
    def _compute_deny_field_names(self):
        # Lưu tên field để user thường đọc policy không cần quyền trên ir.model.fields
        for rec in self:
            rec.deny_field_names = rec.deny_field_ids.mapped('name')

    @api.model
    @tools.ormcache()
    def _policy_map(self):
        rows = self.search_read([('active', '=', True)],
                                ['model_name', 'description', 'deny_field_names'])
        return {r['model_name']: {'fields_deny': list(r['deny_field_names'] or []),
                                  'description': r['description'] or ''}
                for r in rows}

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self.env.registry.clear_cache()
        return recs

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res
