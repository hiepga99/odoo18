from odoo.addons.ai_mcp.core.tools_generic import TOOLS

PUBLIC_KEYS = ('name', 'description', 'inputSchema', 'annotations')

# Tool đăng ký ngoài không khai annotations -> mặc định bảo thủ (destructive)
# để harness luôn hỏi người dùng; đặt ở điểm gom cuối vì override _get_tools
# có thể nối tool SAU super().
CONSERVATIVE_ANNOTATIONS = {'readOnlyHint': False, 'destructiveHint': True,
                            'idempotentHint': False, 'openWorldHint': False}


class UnknownToolError(KeyError):
    """Raised when tools/call names a tool that is not registered."""


def _tools(env):
    # env=None: tool tĩnh (test/unit); có env: qua provider để module khác thêm tool động
    return env['ai.mcp.tool.provider']._get_tools() if env is not None else list(TOOLS)


def list_tools(env=None):
    out = []
    for t in _tools(env):
        d = {k: t[k] for k in PUBLIC_KEYS if k in t}
        d.setdefault('annotations', dict(CONSERVATIVE_ANNOTATIONS))
        out.append(d)
    return out


def tools_list_ttl_ms(env):
    return env['ai.mcp.tool.provider']._get_tools_list_ttl_ms()


def dispatch(env, name, arguments):
    for t in _tools(env):
        if t['name'] == name:
            return t['handler'](env, arguments or {})
    raise UnknownToolError(name)
