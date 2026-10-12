AI Document Upload
==================

This addon owns the document upload feature only.  Its MVP boundaries are:

* Model: ``models/document.py`` stores and validates document files.
* View: ``views/`` contains the list, form and multi-upload dialog.
* Presenter: ``wizards/document_multi_upload.py`` handles user input/actions.
* Application service: ``services/document_upload_service.py`` creates documents.

The detail form previews PDF files with Odoo's built-in PDF viewer.  Other
supported formats remain downloadable and use the RAG extension's extracted
text preview after indexing.

RAG indexing, vector status and chunk previews intentionally live in the separate
``ai_rag_document`` addon, which extends this addon.
