import json
from odoo.tests import HttpCase, tagged
from .test_auth import _make_key


@tagged('post_install', '-at_install', 'ai_mcp')
class TestPermissions(HttpCase):
    """Nghiệm thu ARC-1: 2 user khác quyền → kết quả khác nhau, không dữ liệu thừa."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group = cls.env['res.groups'].create({'name': 'MCP Restricted'})
        cls.user_a = cls.env['res.users'].create({
            'name': 'User A (restricted)', 'login': 'perm_a',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, group.id])],
        })
        cls.user_b = cls.env['res.users'].create({
            'name': 'User B (full)', 'login': 'perm_b',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.p_visible = cls.env['res.partner'].create({'name': 'PERM Visible'})
        cls.p_hidden = cls.env['res.partner'].create({'name': 'PERM Hidden Secret'})
        # user trong group Restricted chỉ thấy partner tên có 'Visible'
        cls.env['ir.rule'].create({
            'name': 'mcp restricted partners',
            'model_id': cls.env['ir.model']._get_id('res.partner'),
            'groups': [(6, 0, [group.id])],
            'domain_force': "[('name', 'like', 'PERM Visible')]",
        })
        cls.key_a = _make_key(cls.env, cls.user_a, 'mcp-perm-a')
        cls.key_b = _make_key(cls.env, cls.user_b, 'mcp-perm-b')

    def _search(self, key):
        r = self.url_open('/mcp', data=json.dumps({
            'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
            'params': {'name': 'odoo_search_read', 'arguments': {
                'model': 'res.partner',
                'domain': [['name', 'like', 'PERM %']],
                'fields': ['name'],
            }},
        }).encode(), headers={'Content-Type': 'application/json',
                              'Authorization': f'Bearer {key}'})
        result = json.loads(r.content)['result']
        payload = json.loads(result['content'][0]['text'])
        return [rec['name'] for rec in payload.get('records', [])]

    def test_same_query_different_results_by_rights(self):
        names_a = self._search(self.key_a)
        names_b = self._search(self.key_b)
        self.assertEqual(names_a, ['PERM Visible'])            # A: đúng phạm vi, không thừa
        self.assertIn('PERM Hidden Secret', names_b)           # B: thấy đủ
        self.assertNotIn('PERM Hidden Secret', names_a)        # A: KHÔNG dữ liệu thừa

    def test_swapped_key_cannot_impersonate(self):
        # key của A luôn ra danh tính A — không tồn tại tham số uid để giả mạo
        names = self._search(self.key_a)
        self.assertNotIn('PERM Hidden Secret', names)
