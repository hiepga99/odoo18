def migrate(cr, version):
    """Give documents created before progress tracking a meaningful value."""
    cr.execute(
        """
        UPDATE ai_rag_document
           SET rag_progress = CASE
                   WHEN rag_status = 'indexed' THEN 100
                   WHEN rag_status = 'processing' THEN GREATEST(rag_progress, 5)
                   ELSE 0
               END,
               rag_progress_stage = CASE
                   WHEN rag_status = 'indexed' THEN 'Hoàn tất - sẵn sàng tra cứu'
                   WHEN rag_status = 'processing' THEN 'Worker đang xử lý tài liệu'
                   WHEN rag_status = 'error' THEN 'Xử lý thất bại'
                   WHEN rag_status = 'delete_pending' THEN 'Đang chờ xóa dữ liệu tìm kiếm'
                   WHEN rag_status = 'disabled' THEN 'Tra cứu AI đã tắt'
                   ELSE 'Đang chờ worker nhận tài liệu'
               END
        """
    )
