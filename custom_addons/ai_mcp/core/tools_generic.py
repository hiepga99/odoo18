from odoo.exceptions import MissingError
from odoo.addons.ai_mcp.models.policy import PolicyError

# Ghi chú description: viết cho LLM — kèm ví dụ domain.
SELECTION_LIMIT = 20   # trần số selection value trả về mỗi field trong describe_model

DOMAIN_HINT = (
    'Domain là JSON array chuẩn Odoo, ví dụ: '
    '[["state","=","sale"]] hoặc [["create_date",">=","2026-01-01"],["partner_id.name","ilike","ACME"]]'
)


def _schema(props, required=None):
    return {'type': 'object', 'properties': props, 'required': required or []}


def list_models(env, args):
    query = (args.get('query') or '').lower()
    models = []
    for model, info in sorted(env['ai.mcp.policy']._get_policy().items()):
        # `model in env` = đã cài; has_access = ACL đọc của chính user này
        if model not in env or not env[model].has_access('read'):
            continue
        # policy có thể mang mô tả viết cho LLM (policy-as-data); mặc định dùng _description
        desc = info.get('description') or env[model]._description or model
        if not query or query in model.lower() or query in desc.lower():
            models.append({'model': model, 'description': desc})
    return {'models': models}


def describe_model(env, args):
    model = args['model']
    policy = env['ai.mcp.policy']
    policy.check_model(model)
    allowed = set(policy.filter_fields(model, None))
    meta = env[model].fields_get(attributes=['type', 'string', 'relation', 'selection'])
    fields = {}
    for name, attrs in meta.items():
        if name not in allowed:
            continue
        attrs = {k: v for k, v in attrs.items() if v}
        selection = attrs.get('selection') or []
        if len(selection) > SELECTION_LIMIT:
            # selection quá dài (vd tz ~600 giá trị) làm phình payload — cắt gọn cho LLM
            attrs['selection_count'] = len(selection)
            attrs['selection'] = selection[:SELECTION_LIMIT]
        fields[name] = attrs
    return {'fields': fields}


def search_read(env, args):
    model = args['model']
    policy = env['ai.mcp.policy']
    policy.check_model(model)
    policy.check_query(model, args.get('domain'), args.get('order'))
    requested = args.get('fields')
    fields = policy.filter_fields(model, requested)
    # Explicit fields all stripped by deny/ACL → do NOT call ORM with [] (reads ALL).
    if requested and not fields:
        return {'records': [], 'count_returned': 0, 'has_more': False}
    limit = policy.clamp_limit(args.get('limit'))
    # lấy dư 1 record để has_more chính xác khi kết quả == limit
    records = env[model].search_read(
        args.get('domain') or [], fields, limit=limit + 1,
        offset=args.get('offset') or 0, order=args.get('order') or None)
    return {'records': records[:limit], 'count_returned': min(len(records), limit),
            'has_more': len(records) > limit}


def read(env, args):
    model = args['model']
    policy = env['ai.mcp.policy']
    policy.check_model(model)
    requested = args.get('fields')
    fields = policy.filter_fields(model, requested)
    if requested and not fields:
        return {'records': []}
    return {'records': env[model].browse(args['ids']).read(fields)}


def search_count(env, args):
    model = args['model']
    policy = env['ai.mcp.policy']
    policy.check_model(model)
    policy.check_query(model, args.get('domain'))
    return {'count': env[model].search_count(args.get('domain') or [])}


def read_group(env, args):
    model = args['model']
    policy = env['ai.mcp.policy']
    policy.check_model(model)
    policy.check_query(model, args.get('domain'))
    groupby = policy.filter_groupby_fields(model, args.get('groupby') or [])
    if not groupby:
        raise PolicyError(
            "groupby rỗng sau khi lọc field bị cấm/không truy cập được. "
            "Chọn field groupby nằm trong phạm vi policy.")
    aggregates = policy.filter_groupby_fields(
        model, args.get('aggregates') or ['__count'])
    if not aggregates:
        aggregates = ['__count']
    groups = env[model].read_group(
        args.get('domain') or [], aggregates, groupby, lazy=False)
    return {'groups': groups}


def get_record_url(env, args):
    model = args['model']
    env['ai.mcp.policy'].check_model(model)
    record = env[model].browse(int(args['id'])).exists()
    if not record:
        raise MissingError("Record không tồn tại hoặc đã bị xóa.")
    record.check_access('read')
    # URL tuyệt đối (get_base_url = web.base.url) để agent trả link dùng được ngay
    return {'url': f"{record.get_base_url()}/odoo/{model}/{record.id}"}


TOOLS = [
    {'name': 'odoo_list_models',
     'description': 'List queryable Odoo models (allowlisted). Start here to discover data.',
     'inputSchema': _schema({'query': {'type': 'string'}}),
     'handler': list_models},
    {'name': 'odoo_describe_model',
     'description': 'Get field definitions (type, label, relation, selection) of a model.',
     'inputSchema': _schema({'model': {'type': 'string'}}, ['model']),
     'handler': describe_model},
    {'name': 'odoo_search_read',
     'description': 'Search records by domain and read field values, paginated. ' + DOMAIN_HINT,
     'inputSchema': _schema({
         'model': {'type': 'string'}, 'domain': {'type': 'array'},
         'fields': {'type': 'array', 'items': {'type': 'string'}},
         'limit': {'type': 'integer'}, 'offset': {'type': 'integer'},
         'order': {'type': 'string'}}, ['model']),
     'handler': search_read},
    {'name': 'odoo_read',
     'description': 'Read records by ids.',
     'inputSchema': _schema({
         'model': {'type': 'string'},
         'ids': {'type': 'array', 'items': {'type': 'integer'}},
         'fields': {'type': 'array', 'items': {'type': 'string'}}},
         ['model', 'ids']),
     'handler': read},
    {'name': 'odoo_search_count',
     'description': 'Count records matching a domain. ' + DOMAIN_HINT,
     'inputSchema': _schema({'model': {'type': 'string'},
                             'domain': {'type': 'array'}}, ['model']),
     'handler': search_count},
    {'name': 'odoo_read_group',
     'description': ('Aggregate records (GROUP BY) for reports, e.g. revenue by month. '
                     + DOMAIN_HINT),
     'inputSchema': _schema({
         'model': {'type': 'string'}, 'domain': {'type': 'array'},
         'groupby': {'type': 'array', 'items': {'type': 'string'}},
         'aggregates': {'type': 'array', 'items': {'type': 'string'}}},
         ['model', 'groupby']),
     'handler': read_group},
    {'name': 'odoo_get_record_url',
     'description': 'Build a deep-link URL to open a record in Odoo web.',
     'inputSchema': _schema({'model': {'type': 'string'},
                             'id': {'type': 'integer'}}, ['model', 'id']),
     'handler': get_record_url},
]

# MCP tool annotations (spec 2025-03-26+): harness dùng để quyết định có hỏi người dùng trước khi chạy.
READ_ONLY_ANNOTATIONS = {'readOnlyHint': True, 'destructiveHint': False,
                         'idempotentHint': True, 'openWorldHint': False}
for _tool in TOOLS:
    _tool.setdefault('annotations', dict(READ_ONLY_ANNOTATIONS))
