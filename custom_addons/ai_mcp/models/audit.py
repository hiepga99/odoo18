import logging
from datetime import timedelta
from functools import wraps

from odoo import api, fields, models
from odoo.modules.registry import Registry
from odoo.sql_db import BaseCursor

_logger = logging.getLogger(__name__)


def after_commit(func):
    """Run ``func`` after the current transaction commits, on a fresh cursor."""

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        assert isinstance(self.env.cr, BaseCursor)
        dbname, context, uid, su = self.env.cr.dbname, self.env.context, self.env.uid, self.env.su

        @self.env.cr.postcommit.add
        def called_after():
            with Registry(dbname).cursor() as cr:
                env = api.Environment(cr, uid, context, su=su)
                try:
                    func(self.with_env(env), *args, **kwargs)
                except Exception as e:  # noqa: BLE001 - audit must never break the request
                    _logger.warning("after_commit failed for %s: %s", self, e)

    return wrapped

RETENTION_DAYS_PARAM = 'ai_mcp.audit_retention_days'
DEFAULT_RETENTION_DAYS = 90


class AiMcpAudit(models.Model):
    _name = 'ai.mcp.audit'
    _description = 'MCP Audit Log'
    _order = 'id desc'

    user_id = fields.Many2one('res.users', required=True, index=True, readonly=True)
    client = fields.Char(readonly=True, help='key index — phân biệt client/key nào gọi')
    tool = fields.Char(readonly=True, index=True)
    model = fields.Char(readonly=True)
    status = fields.Selection(
        [('ok', 'OK'), ('error', 'Error'),
         ('denied', 'Denied'), ('rate_limited', 'Rate limited')],
        readonly=True, index=True)
    duration_ms = fields.Integer(readonly=True)
    record_count = fields.Integer(readonly=True)
    detail = fields.Char(readonly=True, help='domain/ids cắt gọn — không chứa dữ liệu record')

    def log(self, **vals):
        # Ghi SAU commit trên cursor riêng: INSERT rời
        # critical path, và audit lỗi chỉ warning — không làm hỏng response.
        self._log_after_commit(vals)

    @after_commit
    def _log_after_commit(self, vals):
        # sudo: user thường không có quyền create model này (ngoại lệ no-sudo có chủ đích)
        self.sudo().create(vals)

    @api.autovacuum
    def _gc_expired_logs(self):
        # Retention: chạy theo cron ir.autovacuum daily của base
        param = self.env['ir.config_parameter'].sudo().get_param(
            RETENTION_DAYS_PARAM, DEFAULT_RETENTION_DAYS)
        try:
            days = int(param)
        except (TypeError, ValueError):
            days = DEFAULT_RETENTION_DAYS
        if days <= 0:
            # Chặn misconfig ('' / chữ / số âm) xóa nhầm cả bảng — về mặc định
            days = DEFAULT_RETENTION_DAYS
        cutoff = fields.Datetime.now() - timedelta(days=days)
        self.sudo().search([('create_date', '<', cutoff)]).unlink()
