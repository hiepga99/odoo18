import odoo
from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@odoo.tests.tagged('post_install_l10n', 'post_install', '-at_install')
class TestItPos(TestPointOfSaleCommon):
    def test_order_to_invoice(self):
        partner = self.env['res.partner'].create({
            'name': 'Italian Test Partner',
        })

        company = self.setup_other_company(
            name='Italian Test Company',
            country_id=self.env.ref('base.it').id,
        )['company']

        tax_group = self.env['account.tax.group'].with_company(company).create({
            'name': 'Test Tax Group',
        })
        tax = self.env['account.tax'].with_company(company).create({
            'name': '22 %',
            'amount': 22.0,
            'amount_type': 'percent',
            'tax_group_id': tax_group.id,
        })

        product = self.env['product.product'].with_company(company).create({
            'name': 'Test Product',
            'list_price': 35.25,
            'taxes_id': [(6, 0, tax.ids)],
        })

        pos_config = self.env['pos.config'].with_company(company).create({
            'name': 'Test Pos Config',
            'it_fiscal_printer_ip': '0.0.0.0',
        })
        pos_config.open_ui()
        current_session = pos_config.current_session_id

        pos_order = self.PosOrder.create({
            'company_id': company.id,
            'session_id': current_session.id,
            'partner_id': partner.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': product.id,
                'price_unit': 35.25,
                'qty': 2.0,
                'price_subtotal': 70.51,
                'price_subtotal_incl': 86.02,
                'tax_ids': product.taxes_id,
            })],
            'amount_tax': 15.51,
            'amount_total': 86.02,
            'amount_paid': 86.02,
            'amount_return': 0.0,
        })

        res = pos_order.action_pos_order_invoice()
        invoice = self.env['account.move'].browse(res['res_id'])
        self.assertAlmostEqual(invoice.amount_total, pos_order.amount_total, places=2, msg="Invoice not correct")

        current_session.action_pos_session_closing_control()
