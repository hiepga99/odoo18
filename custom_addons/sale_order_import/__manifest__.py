# -*- coding: utf-8 -*-
{
    'name': "Sale Order Import",
    'summary': "Import sale orders from retailer PDF or Excel files",
    'description': "Create quotations from supermarket purchase orders (PDF) or an Excel template.",
    'author': "ERPViet",
    'website': "https://erpviet.vn",
    'category': 'Sales',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'stock'],
    'external_dependencies': {'python': ['pdfplumber', 'pdfminer', 'pypdf', 'openpyxl', 'xlrd']},
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_import_views.xml',
    ],
    'installable': True,
}
