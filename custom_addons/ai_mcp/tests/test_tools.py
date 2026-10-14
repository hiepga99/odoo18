import json
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo.addons.ai_mcp.core import registry
from odoo.addons.ai_mcp.models.policy import PolicyError


@tagged('post_install', '-at_install', 'ai_mcp')
class TestTools(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Tool User', 'login': 'tool_user',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.uenv = cls.env(user=cls.user)
        cls.partners = cls.env['res.partner'].create(
            [{'name': f'MCPTest Partner {i}'} for i in range(25)])

    def _call(self, name, args):
        return registry.dispatch(self.uenv, name, args)

    def _patch_policy(self, model, fields_deny):
        """Context manager: policy với entry `model` bị ghi đè fields_deny."""
        Policy = self.env.registry['ai.mcp.policy']
        base = self.env['ai.mcp.policy']._get_policy()
        base[model] = {'fields_deny': fields_deny}
        return patch.object(Policy, '_get_policy', return_value=base)

    def test_list_models_filters_by_query(self):
        out = self._call('odoo_list_models', {'query': 'partner'})
        self.assertTrue(any(m['model'] == 'res.partner' for m in out['models']))

    def test_list_models_respects_read_acl(self):
        """User không có quyền đọc model nào thì list_models ẩn model đó."""
        # ir.cron: chỉ base.group_system đọc được — thêm tạm vào allowlist
        with self._patch_policy('ir.cron', []):
            out_user = self._call('odoo_list_models', {})
            out_admin = registry.dispatch(self.env, 'odoo_list_models', {})
        self.assertFalse(any(m['model'] == 'ir.cron' for m in out_user['models']))
        self.assertTrue(any(m['model'] == 'ir.cron' for m in out_admin['models']))

    def test_describe_model_hides_denied(self):
        out = self._call('odoo_describe_model', {'model': 'res.partner'})
        self.assertIn('name', out['fields'])
        self.assertNotIn('image_1920', out['fields'])    # binary không "hiển thị được"

    def test_search_read_pagination(self):
        out = self._call('odoo_search_read', {
            'model': 'res.partner',
            'domain': [['name', 'like', 'MCPTest Partner%']],
        })
        self.assertEqual(out['count_returned'], 20)      # trần mặc định
        self.assertTrue(out['has_more'])

    def test_search_read_limit_cap(self):
        self.env['res.partner'].create(
            [{'name': f'MCPTest Cap {i}'} for i in range(210)])
        out = self._call('odoo_search_read', {
            'model': 'res.partner', 'limit': 9999,
            'domain': [['name', 'like', 'MCPTest Cap%']],
        })
        self.assertEqual(out['count_returned'], 200)
        self.assertTrue(out['has_more'])

    def test_read_by_ids(self):
        ids = self.partners[:2].ids
        out = self._call('odoo_read', {'model': 'res.partner', 'ids': ids})
        self.assertEqual(len(out['records']), 2)

    def test_search_count(self):
        out = self._call('odoo_search_count', {
            'model': 'res.partner',
            'domain': [['name', 'like', 'MCPTest Partner%']],
        })
        self.assertEqual(out['count'], 25)

    def test_read_group(self):
        out = self._call('odoo_read_group', {
            'model': 'res.partner',
            'domain': [['name', 'like', 'MCPTest Partner%']],
            'groupby': ['is_company'],
        })
        self.assertTrue(out['groups'])

    def test_search_read_all_fields_denied_returns_empty(self):
        """Explicit fields fully stripped by denylist must not call ORM with []."""
        with self._patch_policy('res.partner', ['email']):
            out = self._call('odoo_search_read', {
                'model': 'res.partner',
                'fields': ['email'],
                'domain': [['name', 'like', 'MCPTest Partner%']],
            })
        self.assertEqual(out['records'], [])
        self.assertEqual(out['count_returned'], 0)
        self.assertFalse(out['has_more'])

    def test_read_all_fields_denied_returns_empty(self):
        with self._patch_policy('res.partner', ['name']):
            out = self._call('odoo_read', {
                'model': 'res.partner',
                'ids': self.partners[:1].ids,
                'fields': ['name'],
            })
        self.assertEqual(out['records'], [])

    def test_search_read_hr_employee_denied_field(self):
        """If hr installed: requesting only a deny field returns empty (test tự expose model)."""
        if 'hr.employee' not in self.env:
            self.skipTest('hr.employee not available (module hr chưa cài)')
        Config = self.env['ai.mcp.model']
        cfg = Config.search([('model_name', '=', 'hr.employee')]) or Config.create(
            {'model_id': self.env['ir.model']._get_id('hr.employee')})
        ident = self.env['ir.model.fields']._get('hr.employee', 'identification_id')
        cfg.deny_field_ids = [(4, ident.id)]
        # user thường bị chặn từ tầng model-ACL; mục đích test là strip deny-field -> dùng admin
        out = registry.dispatch(self.env, 'odoo_search_read', {
            'model': 'hr.employee',
            'fields': ['identification_id'],
            'limit': 5,
        })
        self.assertEqual(out['records'], [])
        self.assertEqual(out['count_returned'], 0)

    def test_read_group_strips_denied_groupby(self):
        with self._patch_policy('res.partner', ['email']):
            # Mixed: denied email stripped, is_company kept
            out = self._call('odoo_read_group', {
                'model': 'res.partner',
                'domain': [['name', 'like', 'MCPTest Partner%']],
                'groupby': ['email', 'is_company'],
            })
        self.assertTrue(out['groups'])
        for g in out['groups']:
            self.assertIn('is_company', g)

    def test_read_group_empty_groupby_raises(self):
        with self._patch_policy('res.partner', ['is_company']):
            with self.assertRaises(PolicyError) as cm:
                self._call('odoo_read_group', {
                    'model': 'res.partner',
                    'groupby': ['is_company'],
                })
        self.assertIn('groupby', str(cm.exception).lower())

    def test_get_record_url(self):
        out = self._call('odoo_get_record_url',
                         {'model': 'res.partner', 'id': self.partners[0].id})
        self.assertIn(f'/odoo/res.partner/{self.partners[0].id}', out['url'])

    def test_model_outside_allowlist_denied(self):
        with self.assertRaises(PolicyError):
            self._call('odoo_search_read', {'model': 'ir.config_parameter'})

    def test_all_tools_have_schema(self):
        for t in registry.list_tools():
            self.assertTrue(t['description'])
            self.assertEqual(t['inputSchema'].get('type'), 'object')
