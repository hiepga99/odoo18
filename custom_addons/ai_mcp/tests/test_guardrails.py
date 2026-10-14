"""Guardrail của /mcp: denylist trên domain/order, ACL đồng bộ giữa các tool,
default fields an toàn, nén selection, URL tuyệt đối, annotations mặc định.
"""
import json

from odoo import Command
from odoo.exceptions import MissingError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.addons.ai_mcp.core import registry
from odoo.addons.ai_mcp.models.policy import PolicyError
from odoo.addons.ai_mcp.tests.test_auth import _make_key


def _basic_user(env, login):
    return env['res.users'].create({
        'name': 'PR Findings Basic', 'login': login,
        'groups_id': [Command.set([env.ref('base.group_user').id])],
    })


def _deny_partner_email(env):
    cfg = env['ai.mcp.model'].search([('model_name', '=', 'res.partner')])
    email = env['ir.model.fields']._get('res.partner', 'email')
    cfg.deny_field_ids = [Command.set([email.id])]
    return cfg


@tagged('post_install', '-at_install', 'ai_mcp')
class TestGuardrails(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = _basic_user(cls.env, 'mcp_prf_basic')
        cls.uenv = cls.env(user=cls.user)

    # ------------------------------------------------------------------
    # denylist phải áp cho cả domain và order — chặn dò giá trị field bị ẩn
    # ------------------------------------------------------------------

    def test_denied_field_in_domain_rejected_search_read(self):
        _deny_partner_email(self.env)
        with self.assertRaises(PolicyError):
            registry.dispatch(self.env, 'odoo_search_read', {
                'model': 'res.partner', 'domain': [['email', 'ilike', 'a@']], 'limit': 1})

    def test_denied_field_in_domain_rejected_search_count(self):
        _deny_partner_email(self.env)
        with self.assertRaises(PolicyError):
            registry.dispatch(self.env, 'odoo_search_count', {
                'model': 'res.partner', 'domain': [['email', '=', 'x@y.z']]})

    def test_denied_field_in_domain_rejected_read_group(self):
        _deny_partner_email(self.env)
        with self.assertRaises(PolicyError):
            registry.dispatch(self.env, 'odoo_read_group', {
                'model': 'res.partner', 'domain': [['email', '!=', False]],
                'groupby': ['is_company']})

    def test_denied_field_in_order_rejected(self):
        _deny_partner_email(self.env)
        with self.assertRaises(PolicyError):
            registry.dispatch(self.env, 'odoo_search_read', {
                'model': 'res.partner', 'fields': ['name'], 'order': 'email desc', 'limit': 1})

    def test_denied_field_in_any_subdomain_rejected(self):
        # any/all lồng comodel (child_ids -> res.partner): field deny trong subdomain vẫn phải chặn
        _deny_partner_email(self.env)
        with self.assertRaises(PolicyError):
            registry.dispatch(self.env, 'odoo_search_read', {
                'model': 'res.partner',
                'domain': [['child_ids', 'any', [['email', 'ilike', 'a@']]]], 'limit': 1})

    def test_dotted_path_to_denied_field_rejected(self):
        _deny_partner_email(self.env)
        with self.assertRaises(PolicyError):
            registry.dispatch(self.env, 'odoo_search_count', {
                'model': 'res.partner', 'domain': [['child_ids.email', 'ilike', 'a@']]})

    def test_allowed_domain_still_works(self):
        _deny_partner_email(self.env)
        out = registry.dispatch(self.env, 'odoo_search_count', {
            'model': 'res.partner', 'domain': [['name', 'ilike', 'a']]})
        self.assertIsInstance(out['count'], int)

    # ------------------------------------------------------------------
    # bare search_read: default fields chỉ gồm field stored
    # (compute non-stored đọc chéo model gây AccessError cho user ít quyền)
    # ------------------------------------------------------------------

    def test_default_fields_are_stored_only(self):
        fields = self.env['ai.mcp.policy'].filter_fields('res.partner', None)
        meta = self.env['res.partner'].fields_get(fields, attributes=['store'])
        not_stored = [f for f in fields if not meta[f]['store']]
        self.assertFalse(not_stored, f'default fields chứa compute non-stored: {not_stored[:5]}')

    # ------------------------------------------------------------------
    # model-level ACL đồng bộ giữa list_models và các tool còn lại
    # (ir.cron: chỉ group_erp_manager đọc được — user basic phải bị chặn NHẤT QUÁN)
    # ------------------------------------------------------------------

    def _expose_ir_cron(self):
        return self.env['ai.mcp.model'].create({
            'model_id': self.env['ir.model']._get_id('ir.cron')})

    def test_describe_model_respects_model_acl(self):
        self._expose_ir_cron()
        self.assertFalse(self.uenv['ir.cron'].has_access('read'))
        with self.assertRaises(PolicyError):
            registry.dispatch(self.uenv, 'odoo_describe_model', {'model': 'ir.cron'})

    def test_search_read_respects_model_acl_like_list_models(self):
        self._expose_ir_cron()
        listed = [m['model'] for m in registry.dispatch(self.uenv, 'odoo_list_models', {})['models']]
        self.assertNotIn('ir.cron', listed)          # list_models đã ẩn
        with self.assertRaises(PolicyError):         # thì tool khác cũng phải chặn cùng lý do
            registry.dispatch(self.uenv, 'odoo_search_read', {'model': 'ir.cron', 'limit': 1})

    # ------------------------------------------------------------------
    # "Model khả dụng" trong lỗi chỉ gợi ý model user đọc được
    # ------------------------------------------------------------------

    def test_error_suggestions_filtered_by_acl(self):
        self._expose_ir_cron()
        with self.assertRaises(PolicyError) as cm:
            self.uenv['ai.mcp.policy'].check_model('ir.config_parameter')
        suggestion = str(cm.exception).split('Model khả dụng')[-1]
        self.assertIn('res.partner', suggestion)
        self.assertNotIn('ir.cron', suggestion)

    # ------------------------------------------------------------------
    # selection dài phải được nén trong describe_model
    # ------------------------------------------------------------------

    def test_long_selection_compressed(self):
        out = registry.dispatch(self.env, 'odoo_describe_model', {'model': 'res.partner'})
        tz = out['fields'].get('tz')
        self.assertTrue(tz, 'res.partner.tz phải có trong schema')
        self.assertLessEqual(len(tz.get('selection') or []), 20,
                             'selection ~600 múi giờ phải được cắt gọn')
        self.assertGreater(tz.get('selection_count', 0), 100)

    # ------------------------------------------------------------------
    # get_record_url: URL tuyệt đối, record phải tồn tại và đọc được
    # ------------------------------------------------------------------

    def test_record_url_is_absolute(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        partner = self.env['res.partner'].create({'name': 'PRF Url'})
        out = registry.dispatch(self.env, 'odoo_get_record_url',
                                {'model': 'res.partner', 'id': partner.id})
        self.assertTrue(out['url'].startswith(base), out['url'])

    def test_record_url_missing_record_errors(self):
        with self.assertRaises(MissingError):
            registry.dispatch(self.env, 'odoo_get_record_url',
                              {'model': 'res.partner', 'id': 99999999})

    # ------------------------------------------------------------------
    # tool động thiếu annotations phải nhận default bảo thủ (destructive)
    # ------------------------------------------------------------------

    def test_dynamic_tool_gets_conservative_default_annotations(self):
        from unittest.mock import patch
        Provider = self.env.registry['ai.mcp.tool.provider']
        orig = Provider._get_tools

        def with_extra(prov):
            return orig(prov) + [{'name': 'x_no_annotations', 'description': 'ext',
                                  'inputSchema': {'type': 'object', 'properties': {}},
                                  'handler': lambda env, args: {}}]
        with patch.object(Provider, '_get_tools', with_extra):
            tool = next(t for t in registry.list_tools(self.env) if t['name'] == 'x_no_annotations')
        self.assertIn('annotations', tool)
        self.assertTrue(tool['annotations']['destructiveHint'],
                        'tool ngoài không khai annotations phải mặc định destructive (bảo thủ)')

    # ------------------------------------------------------------------
    # has_more đúng khi số record bằng đúng limit
    # ------------------------------------------------------------------

    def test_has_more_false_when_exact_limit(self):
        self.env['res.partner'].create([{'name': f'PRF HasMore {i}'} for i in range(3)])
        out = registry.dispatch(self.env, 'odoo_search_read', {
            'model': 'res.partner', 'domain': [['name', 'like', 'PRF HasMore%']],
            'fields': ['name'], 'limit': 3})
        self.assertEqual(out['count_returned'], 3)
        self.assertFalse(out['has_more'])


@tagged('post_install', '-at_install', 'ai_mcp')
class TestGuardrailsHttp(HttpCase):
    """Request méo phải trả JSON-RPC, không bao giờ 500 HTML."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = _basic_user(cls.env, 'mcp_prf_http')
        cls.key = _make_key(cls.env, cls.user, 'prf-http')

    def _post(self, body):
        return self.url_open('/mcp', data=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json', 'Authorization': f'Bearer {self.key}'})

    def test_params_list_on_tools_call_not_500(self):
        r = self._post({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                        'params': ['not', 'a', 'dict']})
        self.assertEqual(r.status_code, 200, r.text[:200])
        self.assertIn('jsonrpc', json.loads(r.content))

    def test_arguments_list_is_error_not_500(self):
        r = self._post({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
                        'params': {'name': 'odoo_search_read', 'arguments': ['x']}})
        self.assertEqual(r.status_code, 200, r.text[:200])
        self.assertTrue(json.loads(r.content)['result']['isError'])
