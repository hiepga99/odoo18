import base64
import json
from odoo.tests import HttpCase, tagged
from .test_auth import _make_key


@tagged('post_install', '-at_install', 'ai_mcp')
class TestProtocol(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'MCP Proto User', 'login': 'mcp_proto',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.key = _make_key(cls.env, cls.user, 'mcp-proto')

    def _rpc(self, method, params=None, rid=1):
        body = {'jsonrpc': '2.0', 'method': method}
        if params is not None:
            body['params'] = params
        if rid is not None:
            body['id'] = rid
        return self.url_open('/mcp', data=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.key}',
        })

    def test_initialize(self):
        r = self._rpc('initialize', {
            'protocolVersion': '2025-03-26',
            'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '0'},
        })
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.headers.get('Mcp-Session-Id'))
        result = json.loads(r.content)['result']
        self.assertEqual(result['protocolVersion'], '2025-03-26')
        self.assertIn('tools', result['capabilities'])
        self.assertEqual(result['serverInfo']['name'], 'ai_mcp')

    def test_notification_initialized_202(self):
        r = self._rpc('notifications/initialized', rid=None)
        self.assertEqual(r.status_code, 202)

    def test_ping(self):
        r = self._rpc('ping')
        self.assertEqual(json.loads(r.content)['result'], {})

    def test_tools_list_shape(self):
        r = self._rpc('tools/list')
        tools = json.loads(r.content)['result']['tools']
        self.assertIsInstance(tools, list)
        for t in tools:
            self.assertIn('name', t)
            self.assertIn('description', t)
            self.assertIn('inputSchema', t)

    def test_unknown_method_error(self):
        r = self._rpc('resources/list')
        err = json.loads(r.content)['error']
        self.assertEqual(err['code'], -32601)

    def test_unknown_tool_error(self):
        r = self._rpc('tools/call', {'name': 'no_such_tool', 'arguments': {}})
        err = json.loads(r.content)['error']
        self.assertEqual(err['code'], -32602)

    def test_missing_arg_is_error_not_unknown_tool(self):
        """KeyError from missing tool args must be isError, not -32602."""
        r = self._rpc('tools/call', {
            'name': 'odoo_describe_model',
            'arguments': {},  # missing required 'model' → KeyError
        })
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.content)
        self.assertNotIn('error', body)
        result = body['result']
        self.assertTrue(result['isError'])
        payload = json.loads(result['content'][0]['text'])
        self.assertIn('error', payload)
        self.assertIn('model', payload['error'].lower())

    def test_tools_call_policy_error_is_error(self):
        r = self._rpc('tools/call', {
            'name': 'odoo_search_read',
            'arguments': {'model': 'ir.config_parameter'},
        })
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.content)['result']
        self.assertTrue(result['isError'])
        payload = json.loads(result['content'][0]['text'])
        self.assertIn('error', payload)

    def test_get_method_405(self):
        r = self.url_open('/mcp')      # GET
        self.assertEqual(r.status_code, 405)

    def test_health_no_auth(self):
        r = self.url_open('/mcp/health')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.content)['status'], 'ok')


@tagged('post_install', '-at_install', 'ai_mcp')
class TestProtocolModern(HttpCase):
    """Spec 2026-07-28: stateless, không initialize, version/identity trong _meta."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'MCP Modern User', 'login': 'mcp_modern',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.key = _make_key(cls.env, cls.user, 'mcp-modern')

    def _modern(self, method, params=None, version='2026-07-28', headers_extra=None):
        params = dict(params or {})
        params['_meta'] = {
            'io.modelcontextprotocol/protocolVersion': version,
            'io.modelcontextprotocol/clientInfo': {'name': 'test', 'version': '0'},
            'io.modelcontextprotocol/clientCapabilities': {},
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.key}',
            'MCP-Protocol-Version': version,
            'Mcp-Method': method,
        }
        headers.update(headers_extra or {})
        body = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}
        return self.url_open('/mcp', data=json.dumps(body).encode(), headers=headers)

    def test_server_discover(self):
        r = self._modern('server/discover')
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.content)['result']
        self.assertEqual(result['resultType'], 'complete')
        self.assertIn('2026-07-28', result['supportedVersions'])
        self.assertIn('tools', result['capabilities'])
        self.assertEqual(
            result['_meta']['io.modelcontextprotocol/serverInfo']['name'], 'ai_mcp')

    def test_tools_list_cacheable_result(self):
        r = self._modern('tools/list')
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.content)['result']
        self.assertEqual(result['resultType'], 'complete')
        self.assertTrue(result['tools'])
        self.assertGreater(result['ttlMs'], 0)
        self.assertEqual(result['cacheScope'], 'private')

    def test_tools_call_stateless_no_initialize(self):
        r = self._modern('tools/call', {
            'name': 'odoo_search_count',
            'arguments': {'model': 'res.partner'},
        }, headers_extra={'Mcp-Name': 'odoo_search_count'})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('Mcp-Session-Id', r.headers)
        result = json.loads(r.content)['result']
        self.assertEqual(result['resultType'], 'complete')
        self.assertFalse(result['isError'])

    def test_unsupported_version_400_32022(self):
        r = self._modern('tools/list', version='2099-01-01')
        self.assertEqual(r.status_code, 400)
        err = json.loads(r.content)['error']
        self.assertEqual(err['code'], -32022)
        self.assertIn('2026-07-28', err['data']['supported'])
        self.assertEqual(err['data']['requested'], '2099-01-01')

    def test_header_body_version_mismatch_400_32020(self):
        r = self._modern('tools/list',
                         headers_extra={'MCP-Protocol-Version': '2025-06-18'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json.loads(r.content)['error']['code'], -32020)

    def test_mcp_method_mismatch_400_32020(self):
        r = self._modern('tools/list', headers_extra={'Mcp-Method': 'tools/call'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json.loads(r.content)['error']['code'], -32020)

    def test_missing_mcp_name_on_tools_call_400_32020(self):
        r = self._modern('tools/call', {
            'name': 'odoo_search_count',
            'arguments': {'model': 'res.partner'},
        })  # không gửi Mcp-Name
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json.loads(r.content)['error']['code'], -32020)

    def test_mcp_name_base64_sentinel_accepted(self):
        encoded = '=?base64?%s?=' % base64.b64encode(b'odoo_search_count').decode()
        r = self._modern('tools/call', {
            'name': 'odoo_search_count',
            'arguments': {'model': 'res.partner'},
        }, headers_extra={'Mcp-Name': encoded})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(json.loads(r.content)['result']['isError'])

    def test_unknown_method_404_32601(self):
        r = self._modern('resources/list')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(json.loads(r.content)['error']['code'], -32601)

    def test_ping_removed_in_modern(self):
        r = self._modern('ping')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(json.loads(r.content)['error']['code'], -32601)

    def test_legacy_initialize_with_modern_version_falls_back(self):
        """Client legacy xin 2026-07-28 qua initialize -> server trả bản legacy mới nhất."""
        r = self.url_open('/mcp', data=json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
            'params': {'protocolVersion': '2026-07-28', 'capabilities': {},
                       'clientInfo': {'name': 'test', 'version': '0'}},
        }).encode(), headers={'Content-Type': 'application/json',
                              'Authorization': f'Bearer {self.key}'})
        result = json.loads(r.content)['result']
        self.assertEqual(result['protocolVersion'], '2025-06-18')

    def test_malformed_meta_not_dict_is_not_500(self):
        """_meta dạng list/chuỗi chứa key modern không được gây 500 — rơi về legacy."""
        for bad_meta in (['io.modelcontextprotocol/protocolVersion'],
                         'io.modelcontextprotocol/protocolVersion'):
            body = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list',
                    'params': {'_meta': bad_meta}}
            r = self.url_open('/mcp', data=json.dumps(body).encode(), headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.key}'})
            self.assertEqual(r.status_code, 200)
            self.assertIn('result', json.loads(r.content))

    def test_non_string_method_invalid_request(self):
        body = {'jsonrpc': '2.0', 'id': 1, 'method': 123, 'params': {}}
        r = self.url_open('/mcp', data=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.key}'})
        self.assertEqual(json.loads(r.content)['error']['code'], -32600)

    def test_empty_body_400(self):
        # ChatGPT thăm dò endpoint bằng POST rỗng; SDK chuẩn trả 400, 200 làm nó tưởng cần OAuth
        r = self.opener.post(self.base_url() + '/mcp', data=b'', headers={
            'Content-Type': 'application/octet-stream', 'Authorization': f'Bearer {self.key}'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json.loads(r.content)['error']['code'], -32600)
