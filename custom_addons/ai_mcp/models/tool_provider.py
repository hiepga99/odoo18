from odoo import models

TOOLS_LIST_TTL_MS = 60000   # tool list động theo DB (used_in_mcp) -> client cache 1 phút


class AiMcpToolProvider(models.AbstractModel):
    """Nguồn tool cho /mcp: 7 tool đọc generic + server action gắn used_in_mcp.
    Module khác mở rộng bằng _inherit."""
    _name = 'ai.mcp.tool.provider'
    _description = 'AI MCP Tool Provider'

    def _get_tools(self):
        # import lười: tools_generic import models.policy -> tránh vòng lặp import lúc load module
        from odoo.addons.ai_mcp.core.tools_generic import TOOLS
        tools = list(TOOLS)
        user = self.env.user
        Action = self.env['ir.actions.server']
        # sudo: ACL ir.actions.server chỉ group_system; đọc định nghĩa như core run() — code vẫn chạy với env user
        for a in Action.sudo().search([('used_in_mcp', '=', True)]):
            allowed = (a.groups_id & user.groups_id) if a.groups_id \
                else self.env[a.model_name].has_access('write')
            if allowed:
                tools.append(a._mcp_tool())
        return tools

    def _get_tools_list_ttl_ms(self):
        return TOOLS_LIST_TTL_MS
