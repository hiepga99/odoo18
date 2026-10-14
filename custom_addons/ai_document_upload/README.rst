AI Document Upload
==================

This addon owns the document upload feature only. Review it in this order:

1. ``models/document.py`` stores and validates document files.
2. ``wizards/document_multi_upload.py`` validates a batch and creates documents.
3. ``views/`` exposes the list, form and multi-upload dialog.
4. ``security/`` limits records by company and user group.

The detail form previews PDF files with Odoo's built-in PDF viewer.  Other
supported formats remain downloadable and use the RAG extension's extracted
text preview after indexing.

RAG indexing, vector status and chunk previews intentionally live in the separate
``ai_rag_document`` addon, which extends this addon.
