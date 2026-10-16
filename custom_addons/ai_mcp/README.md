# AI MCP Server (`ai_mcp`)

MCP endpoint `/mcp` — tra cứu dữ liệu Odoo **đúng quyền từng user**, read-only, cho mọi MCP client (Cursor, Claude Code, OpenAI Agents SDK, OpenClaw, Inspector…).

- Transport: Streamable HTTP (JSON-RPC 2.0) tại `POST /mcp`
- Auth: `Authorization: Bearer <Odoo API key>` (`res.users.apikeys`, scope `rpc`) — hoặc `?key=<API key>` trên URL cho client không gửi được header
- Health: `GET /mcp/health` (không cần auth)
- 7 tool generic: `odoo_list_models`, `odoo_describe_model`, `odoo_search_read`, `odoo_read`, `odoo_search_count`, `odoo_read_group`, `odoo_get_record_url`
- Policy: allowlist model + denylist field; rate limit 60 req/phút theo `(uid, key)`; audit `ai.mcp.audit`

## Tạo API key

### UI (khuyến nghị cho người dùng)

1. Đăng nhập Odoo bằng **user nội bộ** (không cần admin).
2. Preferences → Account Security → **New API Key**.
3. Scope mặc định `rpc`, tên theo client (vd `mcp-cursor-hiep`, `mcp-dev-test`).
4. Copy key một lần → lưu vào env var, **không commit**.



export ODOO_MCP_KEY='<key vừa in>'
```

Thu hồi: xóa key trên Odoo (per client). Mỗi client nên dùng 1 key riêng.

## Cấu hình client

Thay URL bằng host thật (dev: `http://127.0.0.1:8069/mcp`). Key qua env var.

| Client | Cách cấu hình |
|--------|----------------|
| **Cursor** | `~/.cursor/mcp.json` (hoặc per-project): `url` + `headers.Authorization` |
| **Claude Code** | `claude mcp add --transport http odoo <url> --header "Authorization: Bearer …"` |
| **ChatGPT (Developer mode → Thêm server MCP tùy chỉnh)** | Xác thực chọn **Không xác thực** (không chọn "OAuth hoặc không xác thực": chế độ đó bắt buộc tìm OAuth metadata) → URL `https://<host>/mcp?key=<API key>` |
| **Claude.ai / Claude Desktop (Connectors)** | Không gửi được header, không có OAuth → URL `https://<host>/mcp?key=<API key>` (cấp key riêng, thu hồi được) |
| **OpenAI** (Responses / Agents SDK) | MCP tool với `server_url` + `headers` |
| **OpenClaw** | Multi-tenant tiêm `Authorization: Bearer` theo user session |
| **MCP Inspector** | Transport Streamable HTTP, URL `/mcp`, header `Authorization` |

### Cursor (`mcp.json`)

```json
{
  "mcpServers": {
    "odoo": {
      "url": "http://127.0.0.1:8069/mcp",
      "headers": { "Authorization": "Bearer ${ODOO_MCP_KEY}" }
    }
  }
}
```

### Claude Code

```bash
claude mcp add --transport http odoo http://127.0.0.1:8069/mcp \
  --header "Authorization: Bearer ${ODOO_MCP_KEY}"
```

### OpenAI Agents / Responses

```python
tools=[{
    "type": "mcp",
    "server_label": "odoo",
    "server_url": "http://127.0.0.1:8069/mcp",
    "headers": {"Authorization": f"Bearer {os.environ['ODOO_MCP_KEY']}"},
}]
```

### Headers chung

| Header | Bắt buộc | Ghi chú |
|--------|----------|---------|
| `Authorization: Bearer <key>` | Có (mọi `POST /mcp`) | Key sai/thu hồi → **401**, không fallback |
| `Content-Type: application/json` | Có | JSON-RPC body |
| `Mcp-Session-Id` | Không (server trả khi `initialize`) | Client có thể lưu; server không bắt buộc |

## Protocol (dual-era)

Server phục vụ đồng thời hai thế hệ client trên cùng `POST /mcp`:

- **Modern — spec `2026-07-28`** (stateless): không cần `initialize`. Mỗi request
  mang version/identity trong `params._meta` (`io.modelcontextprotocol/protocolVersion`,
  `.../clientInfo`, `.../clientCapabilities`) và các header `MCP-Protocol-Version`,
  `Mcp-Method`, `Mcp-Name` (với `tools/call`). Có `server/discover`. Version không
  hỗ trợ → HTTP 400, JSON-RPC `-32022` kèm `data.supported`; header lệch body →
  400, `-32020`; method lạ → 404, `-32601`.
- **Legacy — `2024-11-05` / `2025-03-26` / `2025-06-18`**: `initialize` handshake
  như cũ (Claude Desktop, Cursor bản hiện tại), `Mcp-Session-Id` chỉ phát ở era này.

## Policy — mở rộng từ module khác

Policy là **dữ liệu**: record `ai.mcp.model` (menu Settings → Technical → AI MCP → Models): bật/tắt model,
mô tả cho LLM, field bị ẩn. Bộ mặc định `DEFAULT_POLICY` (`models/policy.py`) gồm contacts, company, product
(+ pricelist, category, uom), sale/purchase (+ lines), account.move (+ lines, payment), stock (quant, picking,
move, lot, warehouse, location), hr (employee ẩn PII/ID/bank, department, job), calendar, crm, helpdesk — chỉ tạo
record cho model đã cài (`_bootstrap_default_policy`: post_init_hook lúc cài, migration `18.0.1.1.0` khi nâng cấp;
không ghi đè record admin đã sửa). Thêm model khác: tạo record trên UI, hoặc
module khác thêm/sửa phạm vi bằng code mà không đụng `ai_mcp`:

```python
class AiMcpPolicy(models.AbstractModel):
    _inherit = 'ai.mcp.policy'

    def _get_policy(self):
        policy = super()._get_policy()
        policy['hr.employee']['fields_deny'].append('salary_expected')
        policy['my.model'] = {'fields_deny': []}
        return policy
```

`odoo_list_models` chỉ trả model mà user hiện tại có quyền đọc (`has_access('read')`).

## Audit & retention

- Audit ghi **sau COMMIT** trên cursor riêng (decorator `after_commit` trong `models/audit.py`) —
  không nằm trên critical path của request; audit lỗi chỉ warning, không hỏng response.
- Retention: row quá `ai_mcp.audit_retention_days` (ir.config_parameter, mặc định 90)
  bị dọn hằng ngày qua `ir.autovacuum`.

## Curl smoke (dev, 2026-07-16)

DB: `odoo` · HTTP: `8069` · User key: `mcp_smoke_user` / key name `mcp-dev-test` · Auth header trong log: `Bearer <redacted>`.

```bash
BASE=http://127.0.0.1:8069/mcp
H=(-H "Content-Type: application/json" -H "Authorization: Bearer $ODOO_MCP_KEY")
```

### Checklist kết quả quan sát

| # | Check | Kết quả |
|---|--------|---------|
| 1 | `GET /mcp/health` | **PASS** → `{"status": "ok", "server": "ai_mcp"}` |
| 2 | `POST /mcp` không key | **PASS** → HTTP `401` |
| 3 | `initialize` | **PASS** → `200`, header `Mcp-Session-Id`, `protocolVersion: "2025-03-26"`, `serverInfo.name: "ai_mcp"` |
| 4 | `tools/list` | **PASS** → 7 tool: `odoo_list_models`, `odoo_describe_model`, `odoo_search_read`, `odoo_read`, `odoo_search_count`, `odoo_read_group`, `odoo_get_record_url` |
| 5 | `tools/call` `odoo_search_read` | **PASS** (xem ghi chú dưới) |

#### Lệnh tham chiếu

```bash
# 1. health
curl -s $BASE/health
# → {"status": "ok", "server": "ai_mcp"}

# 2. no auth → 401
curl -s -o /dev/null -w '%{http_code}\n' -X POST $BASE \
  -H "Content-Type: application/json" -d '{}'
# → 401

# 3. initialize
curl -si -X POST $BASE "${H[@]}" -d '{
  "jsonrpc":"2.0","id":1,"method":"initialize",
  "params":{"protocolVersion":"2025-03-26","capabilities":{},
            "clientInfo":{"name":"curl","version":"0"}}
}'
# → Mcp-Session-Id: <uuid>
# → {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-03-26",...}}

# 4. tools/list
curl -s -X POST $BASE "${H[@]}" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | python3 -c "import sys,json; print([t['name'] for t in json.load(sys.stdin)['result']['tools']])"
# → 7 names as above

# 5. tools/call — bare search_read (không fields) cũng OK
curl -s -X POST $BASE "${H[@]}" -d '{
  "jsonrpc":"2.0","id":3,"method":"tools/call",
  "params":{"name":"odoo_search_read",
            "arguments":{"model":"res.partner","limit":3}}
}' | python3 -m json.tool
# → isError: false, count_returned: 3
#    records: Administrator, MCP Smoke User, My Company
```

**Ghi chú bước 5:** Bare `odoo_search_read` without `fields` now filters by field ACL (`Field.is_accessible`) so internal users without Accounting no longer get `AccessError` on restricted partner fields (e.g. `property_account_payable_id`); optional explicit `fields` still works.

## MCP Inspector checklist

```bash
npx @modelcontextprotocol/inspector
```

Trong UI: Transport = **Streamable HTTP**, URL = `http://127.0.0.1:8069/mcp`, Authentication → Header `Authorization: Bearer <key>` → Connect.

| Check | Status |
|-------|--------|
| Connect / initialize OK | **pending human** |
| Tab Tools: đủ 7 tool, schema render đúng | **pending human** |
| Run `odoo_list_models` → allowlist | **pending human** |
| Run `odoo_search_read` model ngoài allowlist (vd `ir.config_parameter`) → `isError: true` + danh sách model khả dụng | **pending human** |

`npx` có sẵn trên máy dev; lần thử tự động (timeout 25s) chưa kịp mở UI (package download bị cắt) — cần người mở Inspector và tick checklist trên.

## Cài / cập nhật addon (dev)

```bash
cd /home/hiephv/AI_project/odoo18-demo
venv/bin/python odoo/odoo-bin -c odoo18.conf -d odoo18 -i ai_mcp --stop-after-init   # đã cài: -u ai_mcp
```
