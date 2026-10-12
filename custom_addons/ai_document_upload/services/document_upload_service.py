from pathlib import PurePosixPath

from odoo import _, models
from odoo.exceptions import ValidationError


MAX_BATCH_FILES = 50


class AiDocumentUploadService(models.AbstractModel):
    """Application service between the upload presenter and domain model."""

    _name = "ai.document.upload.service"
    _description = "AI Document Upload Service"

    def create_from_attachments(self, attachments, *, company, owner):
        attachments = attachments.exists()
        if not attachments:
            raise ValidationError(_("Vui lòng chọn ít nhất một tệp."))
        if len(attachments) > MAX_BATCH_FILES:
            raise ValidationError(_("Mỗi lần chỉ được tải tối đa 50 tệp."))

        values = []
        for attachment in attachments:
            filename = attachment.name or "document"
            title = PurePosixPath(filename.replace("\\", "/")).stem or filename
            values.append(
                {
                    "name": title,
                    "file_name": filename,
                    "file_data": attachment.datas,
                    "company_id": company.id,
                    "owner_id": owner.id,
                }
            )
        return self.env["ai.rag.document"].create(values)
