{
    'name': 'AI MCP Server',
    'summary': 'MCP endpoint /mcp - tra cứu dữ liệu Odoo đúng quyền từng user, cho mọi MCP client',
    'category': 'Productivity',
    'version': '18.0.1.0.0',
    'author': 'Odoo AI Agent Team',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/audit_views.xml',
        'views/mcp_model_views.xml',
        'views/ir_actions_server_views.xml',
        'data/mcp_model_data.xml',
    ],
    'demo': [
        'demo/mcp_actions_demo.xml',
    ],
    'post_init_hook': '_bootstrap_from_legacy_policy',
    'license': 'LGPL-3',
    'installable': True,
}
