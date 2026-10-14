import json
from odoo.tests import HttpCase, tagged


def _make_key(env, user, name='mcp-test'):
    return env['res.users.apikeys'].with_user(user).sudo()._generate('rpc', name, None)


@tagged('post_install', '-at_install', 'ai_mcp')
class TestAuth(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'MCP Test User', 'login': 'mcp_user',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.key = _make_key(cls.env, cls.user)

    def _post(self, headers=None):
        body = b'{"jsonrpc":"2.0","method":"ping","id":1}'
        return self.url_open('/mcp', data=body,
                             headers={'Content-Type': 'application/json', **(headers or {})})

    def test_no_header_401(self):
        self.assertEqual(self._post().status_code, 401)

    def test_bad_key_401(self):
        r = self._post({'Authorization': 'Bearer deadbeef' * 8})
        self.assertEqual(r.status_code, 401)

    def test_good_key_returns_owner(self):
        r = self._post({'Authorization': f'Bearer {self.key}'})
        self.assertEqual(r.status_code, 200)

    def test_revoked_key_401(self):
        key2 = _make_key(self.env, self.user, 'mcp-revoked')
        self.env['res.users.apikeys'].sudo().search(
            [('user_id', '=', self.user.id), ('name', '=', 'mcp-revoked')])._remove()
        r = self._post({'Authorization': f'Bearer {key2}'})
        self.assertEqual(r.status_code, 401)
