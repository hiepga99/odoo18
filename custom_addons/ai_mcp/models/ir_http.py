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
        # shortcut: ?key= cho client không gửi được header (claude.ai Connectors, không có OAuth);
        # key lộ trong log/proxy -> cấp key riêng để thu hồi được. Nâng cấp: OAuth 2.1 khi cần.
        token = (match and match.group(1).strip()) or request.httprequest.args.get('key', '').strip()
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
