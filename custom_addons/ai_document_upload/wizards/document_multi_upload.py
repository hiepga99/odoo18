from pathlib import PurePosixPath

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


MAX_BATCH_FILES = 50


class AiDocumentMultiUploadWizard(models.TransientModel):
    _name = "ai.document.multi.upload.wizard"
    _description = "Upload Many AI Knowledge Documents"

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "ai_document_multi_upload_attachment_rel",
        "wizard_id",
        "attachment_id",
        string="Tệp tài liệu",
        required=True,
    )
    file_count = fields.Integer(string="Số tệp", compute="_compute_file_count")
    company_id = fields.Many2one(
        "res.company",
        string="Công ty",
        required=True,
        default=lambda self: self.env.company,
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Người quản lý",
        required=True,
        default=lambda self: self.env.user,
    )

    @api.depends("attachment_ids")
    def _compute_file_count(self):
        for wizard in self:
            wizard.file_count = len(wizard.attachment_ids)

    def action_upload_documents(self):
        self.ensure_one()
        attachments = self.attachment_ids.exists()
        if not attachments:
            raise ValidationError(_("Vui lòng chọn ít nhất một tệp."))
        if len(attachments) > MAX_BATCH_FILES:
            raise ValidationError(_("Mỗi lần chỉ được tải tối đa 50 tệp."))

        values = []
        for attachment in attachments:
            filename = attachment.name or "document"
            values.append(
                {
                    "name": PurePosixPath(filename.replace("\\", "/")).stem or filename,
                    "file_name": filename,
                    "file_data": attachment.datas,
                    "company_id": self.company_id.id,
                    "owner_id": self.owner_id.id,
                }
            )
        documents = self.env["ai.rag.document"].create(values)
        # The binary fields on the created documents now own persistent copies.
        # Remove only attachments created for this transient wizard.
        attachments.filtered(
            lambda item: item.res_model == self._name and item.res_id == self.id
        ).unlink()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "ai_document_upload.ai_document_action"
        )
        action.update(
            {
                "domain": [("id", "in", documents.ids)],
                "context": {
                    "search_default_my_documents": 1,
                    "upload_success_count": len(documents),
                },
            }
        )
        return action
