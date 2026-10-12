from odoo import api, fields, models


class AiRagChunk(models.Model):
    _name = "ai.rag.chunk"
    _description = "AI RAG Indexed Chunk Preview"
    _order = "document_id, chunk_index, id"

    document_id = fields.Many2one(
        "ai.rag.document",
        string="Tài liệu",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="document_id.company_id",
        string="Công ty",
        store=True,
        index=True,
    )
    vector_id = fields.Char(string="Mã vector", required=True, readonly=True, index=True)
    chunk_index = fields.Integer(string="Thứ tự kỹ thuật", required=True, readonly=True)
    chunk_number = fields.Integer(string="Đoạn số", compute="_compute_friendly_labels")
    page = fields.Integer(string="Trang nguồn", readonly=True)
    page_label = fields.Char(string="Vị trí trong tệp", compute="_compute_friendly_labels")
    source_name = fields.Char(string="Tệp nguồn", readonly=True)
    char_count = fields.Integer(string="Số ký tự", readonly=True)
    text_preview = fields.Text(string="Nội dung đã làm sạch", readonly=True)

    @api.depends("chunk_index", "page", "document_id.name")
    def _compute_friendly_labels(self):
        for chunk in self:
            chunk.chunk_number = chunk.chunk_index + 1
            chunk.page_label = f"Trang {chunk.page}" if chunk.page else "Toàn bộ tài liệu"

    @api.depends("document_id.name", "chunk_index", "page")
    def _compute_display_name(self):
        for chunk in self:
            location = f"trang {chunk.page}" if chunk.page else "không phân trang"
            chunk.display_name = (
                f"{chunk.document_id.display_name} · Đoạn {chunk.chunk_index + 1} · {location}"
            )

    def write(self, vals):
        if not self.env.context.get("rag_worker_update"):
            return False
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get("rag_worker_update"):
            return False
        return super().unlink()
