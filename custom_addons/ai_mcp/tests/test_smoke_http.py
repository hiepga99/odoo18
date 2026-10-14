"""Smoke end-to-end qua HTTP /mcp: health, tools/list, từ chối đúng làn,
denylist strip, và chặn dò field bị ẩn qua domain/order.
Kịch bản hr.employee tự skip khi DB chưa cài hr.
"""
import json

from odoo import Command
from odoo.tests import HttpCase, tagged
from odoo.addons.ai_mcp.tests.test_auth import _make_key


@tagged('post_install', '-at_install', 'ai_mcp')
class TestHttpSmoke(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.basic = cls.env['res.users'].create({
            'name': 'PR Scenario Basic', 'login': 'mcp_prs_basic',
            'groups_id': [Command.set([cls.env.ref('base.group_user').id])],
        })
        cls.basic_key = _make_key(cls.env, cls.basic, 'prs-basic')
        cls.admin_key = _make_key(cls.env, cls.env.ref('base.user_admin'), 'prs-admin')

    def _rpc(self, key, method, params=None, rid=1):
        body = {'jsonrpc': '2.0', 'id': rid, 'method': method}
        if params is not None:
            body['params'] = params
        return self.url_open('/mcp', data=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'})

    def _call(self, key, tool, arguments):
        r = self._rpc(key, 'tools/call', {'name': tool, 'arguments': arguments})
        self.assertEqual(r.status_code, 200, r.text[:200])
        result = json.loads(r.content)['result']
        return result['isError'], json.loads(result['content'][0]['text'])

    # ---- smoke protocol ----

    def test_health_no_auth(self):
        r = self.url_open('/mcp/health')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.content), {'status': 'ok', 'server': 'ai_mcp'})

    def test_tools_list_read_tools_annotated(self):
        r = self._rpc(self.basic_key, 'tools/list')
        tools = json.loads(r.content)['result']['tools']
        read_tools = [t for t in tools if t['name'].startswith('odoo_')]
        self.assertEqual(len(read_tools), 7)
        for t in read_tools:
            self.assertTrue(t['annotations']['readOnlyHint'], t['name'])
            self.assertFalse(t['annotations']['destructiveHint'], t['name'])

    def test_outside_allowlist_clean_refusal_with_guidance(self):
        # từ chối kèm gợi ý — gợi ý phải là model user đọc được
        is_error, payload = self._call(self.basic_key, 'odoo_search_read',
                                       {'model': 'ir.config_parameter', 'limit': 1})
        self.assertTrue(is_error)
        self.assertIn('res.partner', payload['error'])

    def test_denied_field_stripped_from_results(self):
        # denylist strip qua HTTP — kịch bản tương đương trên res.partner
        cfg = self.env['ai.mcp.model'].search([('model_name', '=', 'res.partner')])
        email = self.env['ir.model.fields']._get('res.partner', 'email')
        cfg.deny_field_ids = [Command.set([email.id])]
        self.env['res.partner'].create({'name': 'PRS Deny', 'email': 'secret@x.vn'})
        is_error, payload = self._call(self.admin_key, 'odoo_search_read', {
            'model': 'res.partner', 'fields': ['name', 'email'],
            'domain': [['name', '=', 'PRS Deny']], 'limit': 5})
        self.assertFalse(is_error)
        for rec in payload['records']:
            self.assertNotIn('email', rec, 'field bị deny không được lộ qua HTTP')

    def test_model_without_access_terminal_refusal(self):
        # từ chối terminal: không 500, message không dẫn agent retry
        self.env['ai.mcp.model'].create({'model_id': self.env['ir.model']._get_id('ir.cron')})
        is_error, payload = self._call(self.basic_key, 'odoo_search_read',
                                       {'model': 'ir.cron', 'limit': 1})
        self.assertTrue(is_error)
        self.assertTrue(any(k in payload['error'] for k in ('quyền', 'phạm vi')),
                        payload['error'])

    # ---- dò field bị ẩn qua domain/order (cần hr) ----

    def _hr_ready(self):
        if 'hr.employee' not in self.env:
            self.skipTest('cần DB có module hr')
        Config = self.env['ai.mcp.model']
        cfg = Config.search([('model_name', '=', 'hr.employee')])
        if not cfg:
            cfg = Config.create({'model_id': self.env['ir.model']._get_id('hr.employee')})
        ident = self.env['ir.model.fields']._get('hr.employee', 'identification_id')
        cfg.deny_field_ids = [Command.set([ident.id])]

    def test_denied_field_domain_oracle_blocked(self):
        """search_count với domain trên field bị deny phải bị chặn."""
        self._hr_ready()
        is_error, payload = self._call(self.admin_key, 'odoo_search_count', {
            'model': 'hr.employee', 'domain': [['identification_id', '=', '032099001234']]})
        self.assertTrue(is_error, 'domain trên field bị deny phải bị chặn')
        self.assertNotIn('count', payload)

    def test_denied_field_order_blocked(self):
        """order theo field bị deny phải bị chặn."""
        self._hr_ready()
        is_error, payload = self._call(self.admin_key, 'odoo_search_read', {
            'model': 'hr.employee', 'fields': ['name'],
            'order': 'identification_id desc', 'limit': 5})
        self.assertTrue(is_error, 'order trên field deny phải bị chặn')

    def test_params_list_on_tools_list_valid_jsonrpc(self):
        """params sai kiểu ở tools/list vẫn phải trả JSON-RPC hợp lệ."""
        r = self._rpc(self.basic_key, 'tools/list', ['not', 'a', 'dict'])
        self.assertEqual(r.status_code, 200)
        self.assertIn('result', json.loads(r.content))
