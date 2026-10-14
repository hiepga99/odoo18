from . import controllers
from . import core
from . import models


def _bootstrap_from_legacy_policy(env):
    """Chuyển allowlist/denylist pilot (dict cũ) thành record ai.mcp.model —
    chỉ model đã cài, bỏ qua model đã có record. Idempotent (an toàn khi -u)."""
    from odoo.addons.ai_mcp.models.policy import LEGACY_PILOT_POLICY
    Config = env['ai.mcp.model'].with_context(active_test=False)
    existing = set(Config.search([]).mapped('model_name'))
    for model, info in LEGACY_PILOT_POLICY.items():
        if model not in env or model in existing:
            continue
        deny = env['ir.model.fields'].search([
            ('model', '=', model), ('name', 'in', info.get('fields_deny', []))])
        Config.create({
            'model_id': env['ir.model']._get_id(model),
            'deny_field_ids': [(6, 0, deny.ids)],
        })
