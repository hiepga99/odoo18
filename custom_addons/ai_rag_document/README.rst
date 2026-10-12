AI RAG Documents for Odoo 18 Community
======================================

This addon supplies only the RAG-processing extension of the internal-document
workflow.  Upload, binary validation and the multi-file presenter are owned by
the separate ``ai_document_upload`` addon.  Neither addon depends on Enterprise
Documents.

Features
--------

* Extend uploaded PDF, DOCX, TXT and Markdown records with RAG state.
* Keep processing state and human-readable cleaning metrics in PostgreSQL.
* Mark new or changed files as ``pending`` instead of running embeddings inside
  the upload request.
* Provide model methods for an authenticated MCP worker to claim jobs, fetch
  content and report indexing results.
* Show a manager-friendly processing summary and sanitized HTML cards for the
  cleaned chunks directly on the document detail form.
* Reclaim interrupted ``processing`` jobs instead of leaving them stuck.
* Let an authenticated user list only indexed document IDs visible through Odoo
  access control and record rules.

Processing states
-----------------

``upload/update -> pending -> processing -> indexed``

Failures move to ``error``. Disabling a document moves it through
``delete_pending`` to ``disabled`` after vector cleanup. Deleting a document
from the Odoo UI now hides it immediately, queues vector cleanup, and hard
deletes the Odoo record plus attachment only after ChromaDB confirms deletion.
The user no longer has to disable RAG manually before deleting.

The addon does not import sentence-transformers or ChromaDB into the Odoo
process. Run ``agent-service/scripts/start_rag_local.ps1`` to start Chroma HTTP
and the automatic MCP worker. New uploads are then indexed without another
manual ingest command.

MCP-facing model methods
------------------------

Worker methods require an Odoo administrator or service account:

* ``mcp_claim_pending_documents(limit=10)``
* ``mcp_get_document_payload(document_id)``
* ``mcp_mark_document_indexed(...)`` including storage metadata and previews
* ``mcp_mark_document_error(document_id, error_message)``
* ``mcp_mark_document_vectors_deleted(document_id)``

The per-user query path calls ``mcp_list_readable_document_ids()``. The backend
must preserve the current Odoo user identity and must never trust an allowed-ID
list supplied directly by a browser.
