from __future__ import annotations

from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import UserError


PENDING_STATE = {
    "rag_status": "pending",
    "rag_progress": 0,
    "rag_progress_stage": "Đang chờ worker nhận tài liệu",
    "rag_error_message": False,
}
DISABLED_STATE = {
    "rag_status": "disabled",
    "rag_progress": 0,
    "rag_progress_stage": "Tra cứu AI đã tắt",
    "rag_error_message": False,
}
DELETE_PENDING_STATE = {
    "rag_status": "delete_pending",
    "rag_progress": 0,
    "rag_progress_stage": "Đang chờ xóa dữ liệu tìm kiếm",
}
CLEARED_INDEX = {
    "rag_chunk_count": 0,
    "rag_page_count": 0,
    "rag_clean_char_count": 0,
    "rag_chunk_size": 0,
    "rag_chunk_overlap": 0,
    "rag_embedding_model": False,
    "rag_indexed_at": False,
    "rag_processing_started_at": False,
    "rag_checksum": False,
    "rag_collection": False,
    "rag_storage_backend": False,
    "rag_storage_location": False,
}


class AiRagDocument(models.Model):
    """RAG extension; upload/storage concerns live in ai_document_upload."""

    _inherit = "ai.rag.document"

    rag_enabled = fields.Boolean(string="Cho phép AI tra cứu", default=True, tracking=True)
    rag_status = fields.Selection(
        [
            ("pending", "Chờ xử lý"),
            ("processing", "Đang làm sạch & tạo vector"),
            ("indexed", "Sẵn sàng tra cứu"),
            ("error", "Xử lý lỗi"),
            ("delete_pending", "Chờ xóa dữ liệu tìm kiếm"),
            ("disabled", "Đã tắt"),
        ],
        string="Trạng thái AI",
        default="pending",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    rag_progress = fields.Integer(
        string="Tiến độ xử lý",
        default=0,
        readonly=True,
        help="Phần trăm hoàn thành của pipeline đọc file, làm sạch, embedding và lưu vector.",
    )
    rag_progress_stage = fields.Char(
        string="Công đoạn hiện tại",
        default="Đang chờ worker nhận tài liệu",
        readonly=True,
    )
    rag_chunk_count = fields.Integer(string="Số đoạn văn bản", readonly=True)
    rag_page_count = fields.Integer(string="Số trang/khối đã đọc", readonly=True)
    rag_clean_char_count = fields.Integer(string="Số ký tự sau làm sạch", readonly=True)
    rag_chunk_size = fields.Integer(string="Kích thước đoạn", readonly=True)
    rag_chunk_overlap = fields.Integer(string="Phần chồng lặp", readonly=True)
    rag_embedding_model = fields.Char(string="Mô hình embedding", readonly=True)
    rag_indexed_at = fields.Datetime(string="Xử lý xong lúc", readonly=True)
    rag_processing_started_at = fields.Datetime(string="Bắt đầu xử lý lúc", readonly=True)
    rag_checksum = fields.Char(string="Mã nội dung đã xử lý", readonly=True)
    rag_collection = fields.Char(string="Kho vector", readonly=True)
    rag_storage_backend = fields.Char(string="Công nghệ lưu vector", readonly=True)
    rag_storage_location = fields.Char(string="Vị trí lưu vector", readonly=True)
    rag_error_message = fields.Text(string="Chi tiết lỗi", readonly=True)
    delete_after_vector_cleanup = fields.Boolean(
        string="Xóa tài liệu sau khi dọn vector",
        default=False,
        readonly=True,
        copy=False,
        help=(
            "Được bật khi người dùng xóa tài liệu. RAG worker sẽ xóa vector "
            "trước, sau đó mới xóa hẳn record và file gốc trong Odoo."
        ),
    )
    chunk_preview_ids = fields.One2many(
        "ai.rag.chunk",
        "document_id",
        string="Nội dung đã làm sạch",
        readonly=True,
    )
    rag_clean_preview_html = fields.Html(
        string="Bản tiền xử lý trực quan",
        compute="_compute_rag_clean_preview_html",
        sanitize=True,
    )

    @api.depends(
        "chunk_preview_ids.chunk_index",
        "chunk_preview_ids.page",
        "chunk_preview_ids.char_count",
        "chunk_preview_ids.text_preview",
    )
    def _compute_rag_clean_preview_html(self):
        for document in self:
            chunks = document.chunk_preview_ids.sorted(
                key=lambda item: (item.chunk_index, item.id)
            )
            if not chunks:
                document.rag_clean_preview_html = Markup(
                    '<div class="alert alert-light border">'
                    '<i class="fa fa-file-text-o me-2"/> '
                    "Chưa có nội dung đã tiền xử lý. Hãy chờ tài liệu được index."
                    "</div>"
                )
                continue

            cards = []
            for chunk in chunks[:50]:
                location = _("Trang %s", chunk.page) if chunk.page else _("Toàn bộ tài liệu")
                cards.append(
                    Markup(
                        '<section class="card shadow-sm mb-3 border-0">'
                        '<header class="card-header bg-light d-flex flex-wrap '
                        'justify-content-between align-items-center gap-2">'
                        '<span class="badge rounded-pill text-bg-primary px-3 py-2">'
                        'Đoạn {number}</span>'
                        '<span class="text-muted small">'
                        '<i class="fa fa-file-o me-1"/> {location}'
                        '<span class="mx-2">•</span>{chars} ký tự'
                        '</span></header>'
                        '<div class="card-body">'
                        '<div style="white-space: pre-wrap; line-height: 1.65; '
                        'font-size: 0.98rem;">{content}</div>'
                        '</div></section>'
                    ).format(
                        number=chunk.chunk_index + 1,
                        location=escape(location),
                        chars=chunk.char_count,
                        content=escape(chunk.text_preview or ""),
                    )
                )

            if len(chunks) > 50:
                cards.append(
                    Markup(
                        '<div class="alert alert-warning">Đang hiển thị 50/{total} '
                        'đoạn đầu tiên. Dùng nút “Đoạn đã xử lý” để xem toàn bộ.</div>'
                    ).format(total=len(chunks))
                )
            document.rag_clean_preview_html = Markup("").join(cards)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update(PENDING_STATE if vals.get("rag_enabled", True) else DISABLED_STATE)
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        file_changed = "file_data" in vals or "file_name" in vals
        if file_changed:
            self.mapped("chunk_preview_ids").with_context(rag_worker_update=True).unlink()
            enabled = vals.get("rag_enabled", len(self) == 1 and self.rag_enabled)
            vals.update(CLEARED_INDEX)
            vals.update(PENDING_STATE if enabled else DISABLED_STATE)
        if vals.get("rag_enabled") is True and not file_changed:
            vals.update(PENDING_STATE)
        elif vals.get("rag_enabled") is False:
            vals.update(DELETE_PENDING_STATE)
        return super().write(vals)

    def action_request_reindex(self):
        for document in self:
            if not document.file_data:
                raise UserError(_("Hãy tải tài liệu lên trước khi yêu cầu xử lý RAG."))
        self.write({"rag_enabled": True})
        return True

    def action_disable_rag(self):
        self.write({"rag_enabled": False})
        return True

    def action_enable_rag(self):
        self.write({"rag_enabled": True})
        return True

    def action_view_chunks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Nội dung đã làm sạch - %s", self.display_name),
            "res_model": "ai.rag.chunk",
            "view_mode": "kanban,list,form",
            "domain": [("document_id", "=", self.id)],
            "context": {"create": False, "edit": False, "delete": False},
        }

    def unlink(self):
        if self.env.context.get("rag_worker_delete"):
            return super().unlink()

        needs_vector_cleanup = self.filtered(
            lambda item: item.rag_status
            in {"pending", "processing", "indexed", "error", "delete_pending"}
        )
        safe_to_delete = self - needs_vector_cleanup
        if needs_vector_cleanup:
            # Hide the record immediately. The worker searches with active_test=False,
            # removes Chroma vectors, and only then hard-deletes this record/file.
            needs_vector_cleanup.with_context(rag_worker_update=True).write(
                {
                    **DELETE_PENDING_STATE,
                    "active": False,
                    "rag_enabled": False,
                    "delete_after_vector_cleanup": True,
                    "rag_error_message": False,
                }
            )
        if safe_to_delete:
            super(AiRagDocument, safe_to_delete).unlink()
        return True
