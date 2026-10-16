import base64
import json
import time
import uuid

from odoo import http
from odoo.exceptions import AccessError, UserError, ValidationError, MissingError
from odoo.http import request
from odoo.addons.ai_mcp.core import registry
from odoo.addons.ai_mcp.core import rate_limit
from odoo.addons.ai_mcp.models.policy import PolicyError
from odoo.addons.ai_mcp.core.registry import UnknownToolError

# Dual-era (spec 2026-07-28 §versioning): request mang _meta protocolVersion
# -> modern stateless; request initialize / không _meta -> legacy handshake.
LEGACY_VERSIONS = ('2024-11-05', '2025-03-26', '2025-06-18')
MODERN_VERSION = '2026-07-28'
SUPPORTED_VERSIONS = (MODERN_VERSION,) + tuple(reversed(LEGACY_VERSIONS))
META_VERSION = 'io.modelcontextprotocol/protocolVersion'
META_SERVER_INFO = 'io.modelcontextprotocol/serverInfo'
SERVER_INFO = {'name': 'ai_mcp', 'version': '1.2.0'}


def _decode_mcp_header(value):
    """Giải sentinel '=?base64?...?=' của Mcp-Name (spec §value-encoding)."""
    if value and value.startswith('=?base64?') and value.endswith('?='):
        try:
            return base64.b64decode(value[9:-2]).decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            return None
    return value


class MCPController(http.Controller):

    @http.route('/mcp/health', type='http', auth='none', methods=['GET'], csrf=False)
    def health(self, **kwargs):
        return request.make_json_response({'status': 'ok', 'server': 'ai_mcp'})

    @http.route('/mcp', type='http', auth='ai_mcp',
                methods=['POST'], csrf=False, save_session=False)
    def mcp(self, **kwargs):
        try:
            data = json.loads(request.httprequest.get_data(as_text=True) or '{}')
        except json.JSONDecodeError:
            return self._error(None, -32700, 'Parse error', status=400)
        # body hỏng -> HTTP 400 như SDK chuẩn (ChatGPT thăm dò bằng POST rỗng, 200 làm nó tưởng cần OAuth)
        if not isinstance(data, dict) or data.get('jsonrpc') != '2.0':
            return self._error(None, -32600, 'Invalid request', status=400)

        method, rid, params = data.get('method'), data.get('id'), data.get('params') or {}
        if not isinstance(method, str):
            return self._error(rid, -32600, 'Invalid request', status=400)
        if not isinstance(params, dict):
            params = {}   # list truthy sống sót tới .get() sẽ nổ 500 — chuẩn hoá một chỗ
        meta = params.get('_meta')
        meta = meta if isinstance(meta, dict) else {}
        if META_VERSION in meta:
            return self._mcp_modern(method, rid, params, meta)
        return self._mcp_legacy(method, rid, params)

    # ------------------------------------------------------------------
    # Legacy era: 2024-11-05 .. 2025-06-18 (initialize handshake)
    # ------------------------------------------------------------------

    def _mcp_legacy(self, method, rid, params):
        if method and method.startswith('notifications/'):
            return request.make_json_response('', status=202)

        handlers = {
            'initialize': self._initialize,
            'ping': lambda p: {},
            'tools/list': lambda p: {'tools': registry.list_tools(request.env)},
            'tools/call': self._tools_call,
        }
        if method not in handlers:
            return self._error(rid, -32601, f'Method not found: {method}')
        try:
            result = handlers[method](params)
        except UnknownToolError as e:
            return self._error(rid, -32602, f'Unknown tool: {e}')
        headers = {}
        if method == 'initialize':
            headers['Mcp-Session-Id'] = uuid.uuid4().hex
        return request.make_json_response(
            {'jsonrpc': '2.0', 'id': rid, 'result': result}, headers=headers)

    def _initialize(self, params):
        client_version = params.get('protocolVersion')
        version = client_version if client_version in LEGACY_VERSIONS else LEGACY_VERSIONS[-1]
        return {
            'protocolVersion': version,
            'capabilities': {'tools': {}},
            'serverInfo': dict(SERVER_INFO),
        }

    # ------------------------------------------------------------------
    # Modern era: 2026-07-28 (stateless, version/identity per-request)
    # ------------------------------------------------------------------

    def _mcp_modern(self, method, rid, params, meta):
        headers = request.httprequest.headers
        requested = meta.get(META_VERSION)
        if headers.get('MCP-Protocol-Version') != requested:
            return self._error(rid, -32020, (
                "Header mismatch: MCP-Protocol-Version %r does not match body %r"
                % (headers.get('MCP-Protocol-Version'), requested)), status=400)
        if requested != MODERN_VERSION:
            return self._error(rid, -32022, (
                'Unsupported protocol version. Modern stateless requests support only '
                '2026-07-28; older versions require the legacy initialize handshake.'
            ), status=400, data={'supported': list(SUPPORTED_VERSIONS),
                                 'requested': requested})
        if headers.get('Mcp-Method') != method:
            return self._error(rid, -32020, (
                "Header mismatch: Mcp-Method %r does not match body %r"
                % (headers.get('Mcp-Method'), method)), status=400)
        if method == 'tools/call':
            name = _decode_mcp_header(headers.get('Mcp-Name'))
            if not name or name != params.get('name'):
                return self._error(rid, -32020, (
                    'Header mismatch: Mcp-Name header missing or does not '
                    'match params.name'), status=400)

        handlers = {
            'server/discover': self._discover,
            'tools/list': lambda p: {'tools': registry.list_tools(request.env),
                                     'ttlMs': registry.tools_list_ttl_ms(request.env),
                                     'cacheScope': 'private'},
            'tools/call': self._tools_call,
        }
        if method not in handlers:
            # Modern: unknown method -> 404 + -32601 (spec §protocol-version-header)
            return self._error(rid, -32601, f'Method not found: {method}', status=404)
        try:
            result = handlers[method](params)
        except UnknownToolError as e:
            return self._error(rid, -32602, f'Unknown tool: {e}')
        result['resultType'] = 'complete'
        result.setdefault('_meta', {})[META_SERVER_INFO] = dict(SERVER_INFO)
        return request.make_json_response({'jsonrpc': '2.0', 'id': rid, 'result': result})

    def _discover(self, params):
        return {
            'supportedVersions': list(SUPPORTED_VERSIONS),
            'capabilities': {'tools': {}},
            'instructions': ('Read-only Odoo ERP data. Start with odoo_list_models, '
                             'then odoo_describe_model before querying.'),
            'ttlMs': registry.tools_list_ttl_ms(request.env),
            'cacheScope': 'private',
        }

    # ------------------------------------------------------------------
    # Shared
    # ------------------------------------------------------------------

    def _tools_call(self, params):
        start = time.monotonic()
        name = params.get('name')
        arguments = params.get('arguments')
        if not isinstance(arguments, dict):
            arguments = {}   # non-dict -> coi như thiếu args, tool tự trả isError
        status, record_count = 'ok', 0
        if not rate_limit.check(request.env.uid,
                                getattr(request, 'ai_mcp_key_index', '')):
            is_error, payload, status = True, {
                'error': 'Vượt rate limit (60 req/phút). Chờ ~1 phút rồi thử lại.'}, 'rate_limited'
        else:
            try:
                # savepoint: tool ghi (action plane) lỗi giữa chừng -> rollback phần đã ghi
                with request.env.cr.savepoint():
                    payload = registry.dispatch(request.env, name, arguments)
                is_error = False
                record_count = payload.get('count_returned') or payload.get('count') or 0
            except UnknownToolError:
                raise
            except AccessError:
                is_error, status, payload = True, 'denied', {'error': (
                    "Không đủ quyền trên dữ liệu này. Đây là giới hạn phân quyền, "
                    "đừng thử lại — hãy báo người dùng.")}
            except MissingError:
                is_error, status, payload = True, 'error', {
                    'error': 'Record không tồn tại hoặc đã bị xóa.'}
            except PolicyError as e:
                is_error, status, payload = True, 'denied', {'error': str(e)}
            except (UserError, ValidationError) as e:
                is_error, status, payload = True, 'error', {'error': str(e)}
            except KeyError as e:
                is_error, status, payload = True, 'error', {'error': (
                    f'Invalid or missing argument: {e}')}
            except (ValueError, TypeError) as e:
                is_error, status, payload = True, 'error', {'error': (
                    f"Field/domain không hợp lệ: {e}. "
                    "Dùng odoo_describe_model để xem field đúng.")}
        request.env['ai.mcp.audit'].log(
            user_id=request.env.uid,
            client=getattr(request, 'ai_mcp_key_index', ''),
            tool=name, model=str(arguments.get('model') or ''),
            status=status, duration_ms=int((time.monotonic() - start) * 1000),
            record_count=record_count,
            detail=str(arguments.get('domain') or arguments.get('ids') or '')[:200],
        )
        return {
            'content': [{'type': 'text',
                         'text': json.dumps(payload, ensure_ascii=False, default=str)}],
            'isError': is_error,
        }

    def _error(self, rid, code, message, status=200, data=None):
        err = {'code': code, 'message': message}
        if data is not None:
            err['data'] = data
        return request.make_json_response(
            {'jsonrpc': '2.0', 'id': rid, 'error': err}, status=status)
