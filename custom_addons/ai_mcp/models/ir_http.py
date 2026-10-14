import re

import werkzeug

from odoo import api, models, SUPERUSER_ID
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_ai_mcp(cls):
        header = request.httprequest.headers.get('Authorization', '')
        match = re.match(r'^bearer\s+(.+)$', header, re.IGNORECASE)
        token = match and match.group(1).strip()
        if not token:
            raise werkzeug.exceptions.Unauthorized()
        # verify key cần superuser env (bảng apikeys không có ACL đọc) — ngoại lệ sudo được khoanh vùng
        env = api.Environment(request.env.cr, SUPERUSER_ID, {})
        uid = env['res.users.apikeys']._check_credentials(scope='rpc', key=token)
        if not uid:
            raise werkzeug.exceptions.Unauthorized()
        request.update_env(user=uid)
        request.ai_mcp_key_index = token[:8]   # định danh client cho rate-limit/audit
        request.session.can_save = False
