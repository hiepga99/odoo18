import json

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.addons.ai_mcp.core import registry
from odoo.addons.ai_mcp.core.registry import UnknownToolError
from odoo.addons.ai_mcp.tests.test_auth import _make_key

CREATE_PARTNER_CODE = """
partner = env['res.partner'].create({'name': mcp_args['name'], 'email': mcp_args.get('email')})
mcp_result.update(id=partner.id, name=partner.name)
"""
BOOM_CODE = """
env['res.partner'].create({'name': mcp_args['name']})
raise UserError('boom after write')
"""


def _make_action(env, name='Create contact', model='base.model_res_partner', groups=None, code=CREATE_PARTNER_CODE):
    return env['ir.actions.server'].create({
        'name': name, 'model_id': env.ref(model).id, 'state': 'code', 'code': code,
        'used_in_mcp': True, 'groups_id': [Command.set(groups or [])],
    })


def _users(env):
    member = env['res.users'].create({
        'name': 'MCP Member', 'login': 'mcp_act_member',
        'groups_id': [Command.set([env.ref('base.group_user').id, env.ref('base.group_partner_manager').id])],
    })
    outsider = env['res.users'].create({
        'name': 'MCP Outsider', 'login': 'mcp_act_outsider',
        'groups_id': [Command.set([env.ref('base.group_user').id])],
    })
    return member, outsider


@tagged('post_install', '-at_install', 'ai_mcp')
class TestMcpActions(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.member, cls.outsider = _users(cls.env)
        cls.group = cls.env.ref('base.group_partner_manager')

    def _names(self, user):
        return [t['name'] for t in registry.list_tools(self.env(user=user))]

    def test_generic_tools_are_readonly_annotated(self):
        tools = [t for t in registry.list_tools(self.env) if t['name'].startswith('odoo_')]
        self.assertEqual(len(tools), 7)
        for t in tools:
            self.assertTrue(t['annotations']['readOnlyHint'], t['name'])

    def test_flag_off_by_default_and_not_listed(self):
        action = _make_action(self.env, groups=[self.group.id])
        action.used_in_mcp = False
        self.assertNotIn(action._mcp_tool_name(), self._names(self.member))

    def test_with_groups_listed_only_for_group_member(self):
        action = _make_action(self.env, groups=[self.group.id])
        self.assertIn(action._mcp_tool_name(), self._names(self.member))
        self.assertNotIn(action._mcp_tool_name(), self._names(self.outsider))

    def test_without_groups_requires_write_access_on_model(self):
        # res.users: admin có write, user thường không -> gate mặc định của core run()
        action = _make_action(self.env, name='Touch user', model='base.model_res_users', code="pass")
        self.assertIn(action._mcp_tool_name(), self._names(self.env.ref('base.user_admin')))
        self.assertNotIn(action._mcp_tool_name(), self._names(self.outsider))

    def test_tool_shape(self):
        action = _make_action(self.env, groups=[self.group.id])
        action.help = '<p>values: name (required), email</p>'
        tool = next(t for t in registry.list_tools(self.env(user=self.member)) if t['name'] == action._mcp_tool_name())
        self.assertFalse(tool['annotations']['readOnlyHint'])
        self.assertTrue(tool['annotations']['destructiveHint'])
        self.assertIn('values: name (required), email', tool['description'])
        self.assertIn('res.partner', tool['description'])
        self.assertEqual(set(tool['inputSchema']['properties']), {'ids', 'values'})

    def test_call_runs_as_user_and_returns_result(self):
        action = _make_action(self.env, groups=[self.group.id])
        out = registry.dispatch(self.env(user=self.member), action._mcp_tool_name(),
                                {'values': {'name': 'MCP Test Co', 'email': 'a@b.c'}})
        partner = self.env['res.partner'].browse(out['id'])
        self.assertEqual(partner.name, 'MCP Test Co')
        self.assertEqual(partner.create_uid, self.member)

    def test_call_with_ids_exposes_records(self):
        p = self.env['res.partner'].create({'name': 'Rename me'})
        action = _make_action(self.env, name='Rename', groups=[self.group.id],
                              code="records.write({'name': mcp_args['name']}); mcp_result['ids'] = records.ids")
        out = registry.dispatch(self.env(user=self.member), action._mcp_tool_name(),
                                {'ids': [p.id], 'values': {'name': 'Renamed'}})
        self.assertEqual(out['ids'], [p.id])
        self.assertEqual(p.name, 'Renamed')

    def test_outsider_cannot_call(self):
        action = _make_action(self.env, groups=[self.group.id])
        with self.assertRaises(UnknownToolError):
            registry.dispatch(self.env(user=self.outsider), action._mcp_tool_name(), {'values': {'name': 'X'}})

    def test_action_error_surfaces_as_user_error(self):
        action = _make_action(self.env, groups=[self.group.id], code="raise UserError('nope')")
        with self.assertRaises(UserError):
            registry.dispatch(self.env(user=self.member), action._mcp_tool_name(), {})


@tagged('post_install', '-at_install', 'ai_mcp')
class TestMcpActionsHttp(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.member, _ = _users(cls.env)
        cls.key = _make_key(cls.env, cls.member, 'mcp-actions')
        cls.boom = _make_action(cls.env, name='Boom', groups=[cls.env.ref('base.group_partner_manager').id], code=BOOM_CODE)

    def _rpc(self, method, params, headers=None):
        body = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}
        h = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.key}'}
        h.update(headers or {})
        return self.url_open('/mcp', data=json.dumps(body).encode(), headers=h)

    def test_failure_rolls_back_partial_writes(self):
        r = self._rpc('tools/call', {'name': self.boom._mcp_tool_name(), 'arguments': {'values': {'name': 'Boom Co'}}})
        result = json.loads(r.content)['result']
        self.assertTrue(result['isError'])
        self.assertIn('boom', result['content'][0]['text'])
        self.assertEqual(self.env['res.partner'].search_count([('name', '=', 'Boom Co')]), 0)

    def test_tools_list_includes_action_with_short_ttl(self):
        meta = {'io.modelcontextprotocol/protocolVersion': '2026-07-28'}
        r = self._rpc('tools/list', {'_meta': meta}, headers={'MCP-Protocol-Version': '2026-07-28', 'Mcp-Method': 'tools/list'})
        result = json.loads(r.content)['result']
        self.assertIn(self.boom._mcp_tool_name(), [t['name'] for t in result['tools']])
        self.assertEqual(result['ttlMs'], 60000)
