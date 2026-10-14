from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged
from odoo.addons.ai_mcp.core import registry
from odoo.addons.ai_mcp.models.policy import PolicyError


@tagged('post_install', '-at_install', 'ai_mcp')
class TestPolicyData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Policy Data User', 'login': 'mcp_pd_user',
            'groups_id': [Command.set([cls.env.ref('base.group_user').id])],
        })
        cls.uenv = cls.env(user=cls.user)
        cls.Config = cls.env['ai.mcp.model']
        # không giả định trạng thái DB: chỉ res.partner (data mặc định) được bật khi vào test
        cls.Config.search([('model_name', '!=', 'res.partner'), ('active', 'in', [True, False])]).unlink()
        cls.Config.search([('model_name', '=', 'res.partner')]).write({'deny_field_ids': [Command.clear()]})
        # unlink ở trên nằm trong transaction của class -> ormcache _policy_map có thể
        # rebuild từ trạng thái chưa commit; clear lại sau rollback để không lây class sau
        cls.addClassCleanup(cls.env.registry.clear_cache)

    def _expose(self, xmlid, **vals):
        return self.Config.create(dict(model_id=self.env.ref(xmlid).id, **vals))

    def test_default_data_exposes_res_partner(self):
        self.assertIn('res.partner', self.uenv['ai.mcp.policy']._get_policy())

    def test_policy_reads_exposed_models_from_config(self):
        self.assertNotIn('res.users', self.uenv['ai.mcp.policy']._get_policy())
        rec = self._expose('base.model_res_users')
        self.assertIn('res.users', self.uenv['ai.mcp.policy']._get_policy())
        rec.active = False
        self.assertNotIn('res.users', self.uenv['ai.mcp.policy']._get_policy())

    def test_deny_fields_from_m2m(self):
        cfg = self.Config.search([('model_name', '=', 'res.partner')])
        email = self.env['ir.model.fields']._get('res.partner', 'email')
        cfg.deny_field_ids = [Command.set([email.id])]
        fields = self.uenv['ai.mcp.policy'].filter_fields('res.partner', ['name', 'email'])
        self.assertEqual(fields, ['name'])

    def test_description_used_in_list_models(self):
        cfg = self.Config.search([('model_name', '=', 'res.partner')])
        cfg.description = 'Khách hàng và liên hệ — dùng để tra thông tin đối tác'
        out = registry.dispatch(self.uenv, 'odoo_list_models', {})
        desc = next(m['description'] for m in out['models'] if m['model'] == 'res.partner')
        self.assertEqual(desc, cfg.description)

    def test_check_model_error_lists_only_exposed_models(self):
        with self.assertRaises(PolicyError) as cm:
            self.uenv['ai.mcp.policy'].check_model('sale.order')
        self.assertIn('res.partner', str(cm.exception))
        self.assertNotIn('sale.order', str(cm.exception).split('Model khả dụng')[-1])

    def test_normal_user_cannot_change_config(self):
        cfg = self.Config.search([('model_name', '=', 'res.partner')])
        with self.assertRaises(AccessError):
            cfg.with_user(self.user).write({'description': 'x'})
        with self.assertRaises(AccessError):
            self.Config.with_user(self.user).create({'model_id': self.env.ref('base.model_res_users').id})

    def test_normal_user_reads_policy_without_sudo(self):
        # user thường không đọc được ir.model/ir.model.fields, nhưng policy phải đọc được
        self.assertFalse(self.uenv['ir.model'].has_access('read'))
        self.assertIn('res.partner', self.uenv['ai.mcp.policy']._get_policy())

    def test_bootstrap_seeds_installed_models_from_legacy_dict(self):
        # Cài module lên môi trường đang dùng dict cũ: record tự sinh cho model đã cài,
        # kèm deny fields — admin không phải cấu hình lại từ đầu.
        from odoo.addons.ai_mcp import _bootstrap_from_legacy_policy
        self.Config.search([]).unlink()
        _bootstrap_from_legacy_policy(self.env)
        cfgs = {c.model_name: c for c in self.Config.search([])}
        self.assertIn('res.partner', cfgs)                       # model base luôn cài
        for name in cfgs:
            self.assertIn(name, self.env)                        # không sinh record cho model chưa cài
        if 'hr.employee' in self.env and 'hr.employee' in cfgs:
            self.assertIn('identification_id', cfgs['hr.employee'].deny_field_names)
        # chạy lại không tạo trùng (idempotent cho -u)
        _bootstrap_from_legacy_policy(self.env)
        self.assertEqual(len(cfgs), self.Config.search_count([]))

    def test_one_config_per_model(self):
        from psycopg2 import IntegrityError
        from odoo.tools import mute_logger
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self._expose('base.model_res_partner')
