from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

from .rag_document import CLEARED_INDEX, DISABLED_STATE


class AiRagDocumentWorker(models.Model):
    """Worker-facing contract for indexing and vector cleanup."""

    _inherit = "ai.rag.document"

    def _ensure_worker_access(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Chỉ RAG worker được ủy quyền mới được thực hiện thao tác này."))

    @api.model
    def _get_worker_document(self, document_id, extra_domain=()):
        self._ensure_worker_access()
        document = self.with_context(active_test=False).search(
            [("id", "=", int(document_id)), *extra_domain], limit=1
        )
        if not document:
            raise AccessError(_("Không tìm thấy tài liệu hoặc không có quyền truy cập."))
        return document

    @api.model
    def worker_claim_pending_documents(self, limit=10):
        self._ensure_worker_access()
        limit = max(1, min(int(limit), 100))
        documents = self.with_context(active_test=False).search(
            [
                "|",
                ("rag_status", "in", ["pending", "delete_pending"]),
                "&",
                ("rag_status", "=", "processing"),
                "|",
                ("rag_processing_started_at", "=", False),
                ("rag_processing_started_at", "<", fields.Datetime.now() - timedelta(minutes=10)),
            ],
            order="id",
            limit=limit,
        )
        jobs = []
        for document in documents:
            operation = "delete" if document.rag_status == "delete_pending" else "index"
            if operation == "index":
                document.with_context(rag_worker_update=True).write(
                    {
                        "rag_status": "processing",
                        "rag_progress": 5,
                        "rag_progress_stage": "Worker đã nhận tài liệu",
                        "rag_processing_started_at": fields.Datetime.now(),
                    }
                )
            jobs.append(
                {
                    "operation": operation,
                    "document_id": document.id,
                    "company_id": document.company_id.id,
                    "checksum": document.content_checksum or "",
                    "file_name": document.file_name,
                }
            )
        return jobs

    @api.model
    def worker_update_document_progress(self, document_id, progress, stage=""):
        """Receive coarse-grained pipeline progress from the authorized RAG worker."""
        document = self._get_worker_document(document_id)
        if document.delete_after_vector_cleanup or document.rag_status != "processing":
            return {"updated": False, "reason": "document_not_processing"}
        document.with_context(rag_worker_update=True).write(
            {
                "rag_progress": max(0, min(int(progress), 99)),
                "rag_progress_stage": (stage or _("Đang xử lý tài liệu"))[:255],
            }
        )
        return {"updated": True}

    @api.model
    def worker_get_document_payload(self, document_id):
        document = self._get_worker_document(
            document_id, (("rag_enabled", "=", True),)
        )
        attachment = document._get_binary_attachment()
        encoded = document.file_data or b""
        if isinstance(encoded, bytes):
            encoded = encoded.decode("ascii")
        return {
            "document_id": document.id,
            "attachment_id": attachment.id,
            "company_id": document.company_id.id,
            "file_name": document.file_name,
            "mimetype": document.mimetype or "application/octet-stream",
            "checksum": document.content_checksum or "",
            "content_base64": encoded,
        }

    @api.model
    def worker_mark_document_indexed(
        self,
        document_id,
        chunk_count,
        checksum,
        collection,
        storage_backend="ChromaDB",
        storage_location="",
        chunk_previews=None,
        page_count=0,
        clean_char_count=0,
        chunk_size=0,
        chunk_overlap=0,
        embedding_model="",
    ):
        document = self._get_worker_document(document_id)
        if document.delete_after_vector_cleanup or document.rag_status == "delete_pending":
            return {"updated": False, "reason": "delete_requested"}
        if checksum and document.content_checksum != checksum:
            document.with_context(rag_worker_update=True).write(
                {
                    "rag_status": "pending",
                    "rag_progress": 0,
                    "rag_progress_stage": "Tài liệu đã thay đổi, đang chờ xử lý lại",
                }
            )
            return {"updated": False, "reason": "document_changed"}
        previews = list(chunk_previews or [])[:500]
        document.chunk_preview_ids.with_context(rag_worker_update=True).unlink()
        preview_values = []
        for position, preview in enumerate(previews):
            preview_values.append(
                {
                    "document_id": document.id,
                    "vector_id": str(preview.get("vector_id") or f"{document.id}-{position}"),
                    "chunk_index": int(preview.get("chunk_index", position)),
                    "page": max(0, int(preview.get("page", 0))),
                    "source_name": str(preview.get("source_name") or document.file_name)[:255],
                    "char_count": max(0, int(preview.get("char_count", 0))),
                    "text_preview": str(preview.get("text_preview") or "")[:2000],
                }
            )
        if preview_values:
            self.env["ai.rag.chunk"].with_context(rag_worker_update=True).create(preview_values)
        document.with_context(rag_worker_update=True).write(
            {
                "rag_status": "indexed",
                "rag_progress": 100,
                "rag_progress_stage": "Hoàn tất - sẵn sàng tra cứu",
                "rag_chunk_count": max(0, int(chunk_count)),
                "rag_page_count": max(0, int(page_count)),
                "rag_clean_char_count": max(0, int(clean_char_count)),
                "rag_chunk_size": max(0, int(chunk_size)),
                "rag_chunk_overlap": max(0, int(chunk_overlap)),
                "rag_embedding_model": (embedding_model or "")[:255],
                "rag_indexed_at": fields.Datetime.now(),
                "rag_processing_started_at": False,
                "rag_checksum": checksum or document.content_checksum,
                "rag_collection": collection or "",
                "rag_storage_backend": storage_backend or "ChromaDB",
                "rag_storage_location": storage_location or "",
                "rag_error_message": False,
            }
        )
        return {"updated": True}

    @api.model
    def worker_mark_document_error(self, document_id, error_message):
        document = self._get_worker_document(document_id)
        if document.delete_after_vector_cleanup:
            document.with_context(rag_worker_update=True).write(
                {
                    "rag_status": "delete_pending",
                    "rag_progress": 0,
                    "rag_progress_stage": "Không thể xóa vector, worker sẽ thử lại",
                    "rag_processing_started_at": False,
                    "rag_error_message": (error_message or _("Lỗi xóa vector không xác định"))[:2000],
                }
            )
            return True
        document.with_context(rag_worker_update=True).write(
            {
                "rag_status": "error",
                "rag_progress_stage": "Xử lý thất bại",
                "rag_processing_started_at": False,
                "rag_error_message": (error_message or _("Lỗi xử lý không xác định"))[:2000],
            }
        )
        return True

    @api.model
    def worker_mark_document_vectors_deleted(self, document_id):
        document = self._get_worker_document(document_id)
        delete_document = document.delete_after_vector_cleanup
        document.with_context(rag_worker_update=True).write(
            {
                **CLEARED_INDEX,
                **DISABLED_STATE,
                "delete_after_vector_cleanup": False,
            }
        )
        document.chunk_preview_ids.with_context(rag_worker_update=True).unlink()
        if delete_document:
            document.with_context(rag_worker_delete=True).unlink()
        return True

    @api.model
    def list_readable_document_ids(self):
        return self.search([("rag_enabled", "=", True), ("rag_status", "=", "indexed")]).ids

    @api.model
    def get_current_rag_scope(self):
        return {
            "user_id": self.env.user.id,
            "company_id": self.env.company.id,
            "allowed_document_ids": self.list_readable_document_ids(),
        }
