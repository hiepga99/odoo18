from __future__ import annotations

import base64
import binascii
import hashlib
import mimetypes
from pathlib import PurePosixPath

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 20 * 1024 * 1024


class AiKnowledgeDocument(models.Model):
    """The upload/domain model; RAG-specific behavior lives in ai_rag_document."""

    _name = "ai.rag.document"
    _description = "AI Knowledge Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char(string="Tên tài liệu", required=True, tracking=True)
    active = fields.Boolean(default=True)
    file_data = fields.Binary(
        string="Tệp tài liệu",
        required=True,
        attachment=True,
        prefetch=False,
    )
    file_name = fields.Char(string="Tên tệp", required=True)
    file_size = fields.Integer(string="Dung lượng (byte)", readonly=True)
    file_size_display = fields.Char(
        string="Dung lượng",
        compute="_compute_file_size_display",
    )
    mimetype = fields.Char(string="Định dạng", readonly=True)
    file_is_pdf = fields.Boolean(
        string="Có thể xem PDF trực tiếp",
        compute="_compute_file_is_pdf",
    )
    content_checksum = fields.Char(
        string="Mã kiểm tra nội dung",
        readonly=True,
        index=True,
        help="SHA-256 dùng để phát hiện tài liệu thay đổi.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Công ty",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Người quản lý",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        index=True,
    )

    @api.depends("file_size")
    def _compute_file_size_display(self):
        for document in self:
            size = max(0, document.file_size or 0)
            if size >= 1024 * 1024:
                document.file_size_display = f"{size / (1024 * 1024):.2f} MB"
            elif size >= 1024:
                document.file_size_display = f"{size / 1024:.1f} KB"
            else:
                document.file_size_display = f"{size} B"

    @api.depends("mimetype", "file_name")
    def _compute_file_is_pdf(self):
        for document in self:
            document.file_is_pdf = (
                document.mimetype == "application/pdf"
                or (document.file_name or "").lower().endswith(".pdf")
            )

    @api.model
    def _decode_upload(self, encoded_value):
        if not encoded_value:
            return b""
        if isinstance(encoded_value, str):
            encoded_value = encoded_value.encode("ascii")
        try:
            return base64.b64decode(encoded_value, validate=False)
        except (ValueError, binascii.Error) as exc:
            raise ValidationError(_("Tệp tải lên không phải dữ liệu base64 hợp lệ.")) from exc

    @api.model
    def _safe_filename(self, filename):
        normalized = (filename or "").replace("\\", "/")
        return PurePosixPath(normalized).name

    @api.model
    def _prepare_file_metadata(self, vals):
        filename = self._safe_filename(vals.get("file_name"))
        if filename:
            vals["file_name"] = filename
        encoded_value = vals.get("file_data")
        if not encoded_value:
            return
        content = self._decode_upload(encoded_value)
        if len(content) > MAX_FILE_SIZE:
            raise ValidationError(_("Dung lượng tối đa cho mỗi tệp là 20 MB."))
        vals.update(
            {
                "file_size": len(content),
                "mimetype": mimetypes.guess_type(filename)[0]
                or "application/octet-stream",
                "content_checksum": hashlib.sha256(content).hexdigest(),
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._prepare_file_metadata(vals)
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "file_data" in vals or "file_name" in vals:
            if "file_data" in vals and not vals.get("file_name") and len(self) == 1:
                vals["file_name"] = self.file_name
            self._prepare_file_metadata(vals)
        return super().write(vals)

    @api.constrains("file_name", "file_data")
    def _check_supported_file(self):
        for document in self:
            suffix = PurePosixPath(self._safe_filename(document.file_name)).suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS:
                raise ValidationError(
                    _("Chỉ hỗ trợ các định dạng PDF, DOCX, TXT và Markdown (MD).")
                )

    def _get_binary_attachment(self):
        self.ensure_one()
        return self.env["ir.attachment"].sudo().search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("res_field", "=", "file_data"),
            ],
            limit=1,
        )
