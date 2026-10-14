import json
from odoo.exceptions import AccessError
from odoo.tests import HttpCase, tagged
from .test_auth import _make_key


@tagged('post_install', '-at_install', 'ai_mcp')
class TestAuditUnit(HttpCase):
    # HttpCase (không phải TransactionCase): cần registry test mode để
    # Registry.cursor() trong callback after_commit trả TestCursor cùng
    # connection — postcommit.run() ghi trong transaction test, rollback sạch.

    def test_log_writes_after_commit_only(self):
        """log() không INSERT trên critical path — chỉ ghi sau commit."""
        Audit = self.env['ai.mcp.audit']
        before = Audit.sudo().search_count([])
        Audit.log(user_id=self.env.uid, client='unittest', tool='odoo_search_count',
                  model='res.partner', status='ok', duration_ms=1,
                  record_count=0, detail='')
        # Chưa commit -> chưa có row
        self.assertEqual(Audit.sudo().search_count([]), before)
        # Test mode: Registry.cursor() trả TestCursor cùng connection ->
        # chạy postcommit thủ công, row ghi trong transaction test, rollback sau test.
        self.env.cr.postcommit.run()
        self.assertEqual(Audit.sudo().search_count([]), before + 1)
        row = Audit.sudo().search([], order='id desc', limit=1)
        self.assertEqual(row.tool, 'odoo_search_count')
        self.assertEqual(row.status, 'ok')
        self.assertEqual(row.user_id.id, self.env.uid)
        self.assertEqual(row.client, 'unittest')
        self.assertEqual(row.model, 'res.partner')
        self.assertEqual(row.duration_ms, 1)
        self.assertEqual(row.record_count, 0)
        self.assertFalse(row.detail)

    def test_gc_invalid_or_negative_param_safe(self):
        """Param hỏng ('' / chữ / âm / 0) không được nổ hoặc xóa nhầm — về mặc định 90."""
        Audit = self.env['ai.mcp.audit'].sudo()
        fresh = Audit.create({'user_id': self.env.uid, 'tool': 'odoo_read', 'status': 'ok'})
        for bad in ('', 'abc', '-5', '0'):
            self.env['ir.config_parameter'].sudo().set_param(
                'ai_mcp.audit_retention_days', bad)
            Audit._gc_expired_logs()
            self.assertTrue(fresh.exists(), f'row bị xóa với param {bad!r}')

    def test_gc_expired_logs(self):
        """Autovacuum xóa row quá hạn retention, giữ row còn hạn."""
        Audit = self.env['ai.mcp.audit'].sudo()
        old = Audit.create({'user_id': self.env.uid, 'tool': 'odoo_read', 'status': 'ok'})
        fresh = Audit.create({'user_id': self.env.uid, 'tool': 'odoo_read', 'status': 'ok'})
        self.env.cr.execute(
            "UPDATE ai_mcp_audit SET create_date = now() - interval '400 days' "
            "WHERE id = %s", [old.id])
        Audit.invalidate_model(['create_date'])
        Audit._gc_expired_logs()
        self.assertFalse(old.exists())
        self.assertTrue(fresh.exists())


@tagged('post_install', '-at_install', 'ai_mcp')
class TestAudit(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Audit User', 'login': 'audit_user',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.key = _make_key(cls.env, cls.user, 'mcp-audit')

    def test_tools_call_does_not_write_audit_synchronously(self):
        """INSERT audit không nằm trên critical path của request.

        TestCursor.commit() xóa postcommit hook không chạy -> trong HttpCase
        row không xuất hiện; phần ghi thật được cover bởi TestAuditUnit."""
        before = self.env['ai.mcp.audit'].sudo().search_count([])
        r = self.url_open('/mcp', data=json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
            'params': {'name': 'odoo_search_count',
                       'arguments': {'model': 'res.partner'}},
        }).encode(), headers={'Content-Type': 'application/json',
                              'Authorization': f'Bearer {self.key}'})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(json.loads(r.content)['result']['isError'])
        self.assertEqual(self.env['ai.mcp.audit'].sudo().search_count([]), before)

    def test_normal_user_cannot_read_audit(self):
        with self.assertRaises(AccessError):
            self.env['ai.mcp.audit'].with_user(self.user).search([])
