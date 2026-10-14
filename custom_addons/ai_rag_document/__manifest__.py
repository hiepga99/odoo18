{
    "name": "AI RAG Document Processing",
    "summary": "Clean, chunk and index uploaded documents for the AI assistant",
    "version": "18.0.2.3.1",
    "category": "Productivity",
    "license": "LGPL-3",
    "author": "Odoo AI Agent Team",
    "depends": ["ai_document_upload"],
    "data": [
        "security/rag_document_security.xml",
        "security/ir.model.access.csv",
        "views/rag_document_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ai_rag_document/static/src/fields/rag_processing_progress/rag_processing_progress.js",
            "ai_rag_document/static/src/fields/rag_processing_progress/rag_processing_progress.xml",
        ],
    },
    "application": True,
    "installable": True,
}
