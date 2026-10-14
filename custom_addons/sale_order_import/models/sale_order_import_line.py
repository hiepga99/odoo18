# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderImportLine(models.Model):
    _name = 'sale.order.import.line'
    _description = 'Sale Order Import Line'

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    import_id = fields.Many2one('sale.order.import', string='Import Sale Order')
    product_id = fields.Many2one('product.product', string='Product')
    product_code = fields.Char('Product Code')
    tax_ids = fields.Many2many('account.tax', string='Tax')
    discount = fields.Float('Discount(%)')
    quantity = fields.Float('Quantity', default=0.0)
    partner_id = fields.Many2one('res.partner', string='Customer')
    description = fields.Char('Description')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse",
                                   default=_default_warehouse_id,
                                   check_company=True)

    attachment_id = fields.Many2one('ir.attachment')
    po_location_code = fields.Char('P/O Location')
    po_name = fields.Char('PO Name')

    so_number = fields.Char()
    order_date = fields.Date()
    delivery_date = fields.Date()

    price_unit = fields.Float()
