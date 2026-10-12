{
    "name": "AI Document Upload",
    "summary": "Manage internal documents and upload many files at once",
    "version": "18.0.1.1.0",
    "category": "Productivity",
    "license": "LGPL-3",
    "author": "Odoo AI Agent Team",
    "depends": ["base", "mail"],
    "data": [
        "security/document_security.xml",
        "security/ir.model.access.csv",
        "views/document_multi_upload_views.xml",
        "views/document_views.xml",
    ],
    "application": True,
    "installable": True,
}
