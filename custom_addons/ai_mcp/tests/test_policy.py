from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged
from odoo.addons.ai_mcp.core import registry
from odoo.addons.ai_mcp.models import policy as policy_mod
from odoo.addons.ai_mcp.models.policy import PolicyError


@tagged('post_install', '-at_install', 'ai_mcp')
class TestPolicy(TransactionCase):

    def setUp(self):
        super().setUp()
        self.policy = self.env['ai.mcp.policy']

    def test_model_in_allowlist_passes(self):
        self.policy.check_model('res.partner')      # dùng trong policy pilot

    def test_model_outside_allowlist_raises(self):
        with self.assertRaises(PolicyError) as cm:
            self.policy.check_model('ir.config_parameter')
        self.assertIn('res.partner', str(cm.exception))   # message kèm model khả dụng

    def test_denylist_field_removed(self):
        if 'hr.employee' in self.policy._get_policy() and 'hr.employee' in self.env:
            fields = self.policy.filter_fields('hr.employee', ['name', 'identification_id'])
            self.assertNotIn('identification_id', fields)
        else:
            fields = self.policy.filter_fields('res.partner', ['name'])
            self.assertEqual(fields, ['name'])

    def test_default_fields_skip_binary(self):
        fields = self.policy.filter_fields('res.partner', None)
        self.assertIn('name', fields)
        self.assertNotIn('image_1920', fields)

    def test_default_fields_respect_field_acl(self):
        """Internal user without accounting: bare search_read must not AccessError."""
        user = self.env['res.users'].create({
            'name': 'MCP No Accounting',
            'login': 'mcp_no_accounting',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        uenv = self.env(user=user)
        fields = uenv['ai.mcp.policy'].filter_fields('res.partner', None)
        self.assertIn('name', fields)
        # Spot-check: accounting property many2one is group-restricted when account is installed
        Partner = uenv['res.partner']
        fname = 'property_account_payable_id'
        if fname in Partner._fields and not Partner._fields[fname].is_accessible(uenv):
            self.assertNotIn(fname, fields)
        # Must not raise AccessError when reading with default fields
        try:
            out = registry.dispatch(uenv, 'odoo_search_read', {
                'model': 'res.partner', 'limit': 3,
            })
        except AccessError:
            self.fail('odoo_search_read with fields=None raised AccessError')
        self.assertLessEqual(out['count_returned'], 3)
        if fname not in fields:
            for rec in out['records']:
                self.assertNotIn(fname, rec)

    def test_clamp_limit(self):
        self.assertEqual(self.policy.clamp_limit(None), 20)
        self.assertEqual(self.policy.clamp_limit(50), 50)
        self.assertEqual(self.policy.clamp_limit(9999), 200)

    def test_read_methods_frozen(self):
        self.assertEqual(policy_mod.READ_METHODS, frozenset(
            {'search_read', 'read', 'search_count', 'read_group',
             'fields_get', 'name_search'}))

    def test_override_via_inherit(self):
        """Module khác override _get_policy() qua _inherit — cơ chế mở rộng chuẩn Odoo."""
        Policy = self.env.registry['ai.mcp.policy']
        base = self.policy._get_policy()
        base['res.partner'] = {'fields_deny': ['email']}
        with patch.object(Policy, '_get_policy', return_value=base):
            fields = self.env['ai.mcp.policy'].filter_fields('res.partner', ['name', 'email'])
        self.assertEqual(fields, ['name'])
