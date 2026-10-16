from . import controllers
from . import core
from . import models


def _bootstrap_default_policy(env):
    """Tạo record ai.mcp.model cho DEFAULT_POLICY — chỉ model đã cài, bỏ qua model đã có record.
    Idempotent: post_init_hook lúc cài, migration gọi lại khi nâng cấp."""
    from odoo import Command
    from odoo.addons.ai_mcp.models.policy import DEFAULT_POLICY
    Config = env['ai.mcp.model'].with_context(active_test=False)
    existing = set(Config.search([]).mapped('model_name'))
    vals_list = []
    for model, info in DEFAULT_POLICY.items():
        if model not in env or model in existing:
            continue
        deny = env['ir.model.fields'].search([
            ('model', '=', model), ('name', 'in', info.get('fields_deny', []))])
        vals_list.append({
            'model_id': env['ir.model']._get_id(model),
            'description': info.get('description'),
            'deny_field_ids': [Command.set(deny.ids)],
        })
    Config.create(vals_list)
