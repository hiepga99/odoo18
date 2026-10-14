import json
import re

from odoo import fields, models
from odoo.tools import html2plaintext

# Hợp đồng chung cho mọi action: bản ghi (ids) + giá trị (values). Không cần schema riêng từng action.
MCP_SCHEMA = {'type': 'object', 'properties': {
    'ids': {'type': 'array', 'items': {'type': 'integer'},
            'description': 'Record ids of the action model to act on (find them with odoo_search_read)'},
    'values': {'type': 'object', 'description': 'Input values for the action (keys: see tool description)'},
}}


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    used_in_mcp = fields.Boolean(
        'Use in MCP', default=False,
        help='Lộ action thành tool GHI qua /mcp. Quyền: Groups nếu có, không thì quyền write trên model '
             '(gate của core run()). Code đọc tham số qua mcp_args, ghi kết quả vào dict mcp_result.')

    def _mcp_tool_name(self):
        slug = re.sub(r'[^a-z0-9]+', '_', (self.name or '').lower()).strip('_')
        return f'act{self.id}_{slug}'   # id giữ duy nhất, slug để LLM đọc được

    def _mcp_tool(self):
        return {
            'name': self._mcp_tool_name(),
            'description': (f"{self.name}. Server action on {self.model_name}: pass 'ids' of {self.model_name} "
                            f"records (find them with odoo_search_read) and/or 'values'. "
                            f"{html2plaintext(self.help or '')}").strip(),
            'inputSchema': MCP_SCHEMA,
            'annotations': {'readOnlyHint': False, 'destructiveHint': True},
            'handler': lambda env, args, aid=self.id: env['ir.actions.server'].browse(aid)._mcp_run(args),
        }

    def _get_eval_context(self, action=None):
        ctx = super()._get_eval_context(action=action)
        ctx.update(mcp_args=self.env.context.get('mcp_args', {}),
                   mcp_result=self.env.context.get('mcp_result', {}))
        return ctx

    def _mcp_run(self, args):
        ids = [int(i) for i in args.get('ids') or []]
        result = {}
        # run(): đọc định nghĩa bằng sudo, gate theo groups_id/quyền write, code chạy với env user
        self.with_context(active_model=self.sudo().model_name, active_ids=ids, active_id=ids[0] if ids else False,
                          mcp_args=dict(args.get('values') or {}), mcp_result=result).run()
        return json.loads(json.dumps(result or {'ok': True, 'ids': ids}, default=str))
