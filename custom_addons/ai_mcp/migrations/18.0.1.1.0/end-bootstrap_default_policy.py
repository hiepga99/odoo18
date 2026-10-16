from odoo import api, SUPERUSER_ID
from odoo.addons.ai_mcp import _bootstrap_default_policy


def migrate(cr, version):
    # end-: chạy sau khi TOÀN BỘ module đã nạp (post- chỉ thấy model nạp trước ai_mcp trong graph)
    _bootstrap_default_policy(api.Environment(cr, SUPERUSER_ID, {}))
