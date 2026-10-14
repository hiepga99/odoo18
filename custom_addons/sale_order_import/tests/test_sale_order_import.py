import base64
from io import BytesIO

import openpyxl

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

HEADER = ['Mã đơn hàng', 'Mã KH', 'Mã PO tham chiếu', 'Ngày đặt hàng', 'Ngày giao hàng dự kiến',
          'Diễn giải', 'Mã sản phẩm', 'Sản phẩm', 'Số lượng']


def xlsx_b64(rows):
    """Build a workbook with the same column layout as static/template/File_mau_import_excel.xlsx."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(HEADER)
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return base64.b64encode(buffer.getvalue())


@tagged('post_install', '-at_install')
class TestImportOrderExcel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Khách import', 'ref': 'KH001'})
        cls.product_a = cls.env['product.product'].create({'name': 'SP A', 'default_code': 'SP001', 'list_price': 10})
        cls.product_b = cls.env['product.product'].create({'name': 'SP B', 'default_code': 'SP002', 'list_price': 20})

    def _import(self, rows, **extra):
        record = self.env['sale.order.import'].create({
            'name': 'Import test', 'import_type': 'excel',
            'file_name': 'import.xlsx', 'file_upload': xlsx_b64(rows), **extra,
        })
        record.action_import_SO_excel()
        return record

    def test_excel_import_creates_lines_then_one_order_per_so_number(self):
        record = self._import([
            # continuation rows of the same order leave both order code and customer code empty
            ['1', 'KH001', 'PO-1', None, None, 'ghi chú', 'SP001', 'SP A', 2],
            [None, None, None, None, None, None, 'SP002', 'SP B', 3],
            ['2', 'KH001', 'PO-2', None, None, None, 'SP001', 'SP A', 5],
            [None, None, None, None, None, None, 'SP001', 'SP A', 1],
        ])
        self.assertEqual(len(record.line_ids), 4)
        self.assertEqual(record.line_ids.mapped('product_id'), self.product_a | self.product_b)
        self.assertTrue(all(line.partner_id == self.partner for line in record.line_ids))

        record.action_confirm()

        self.assertEqual(record.state, 'confirmed')
        self.assertEqual(record.so_count, 2)
        orders = record.sale_order_ids.sorted('client_order_ref')
        self.assertEqual(orders.mapped('client_order_ref'), ['PO-1', 'PO-2'])
        self.assertEqual(orders[0].partner_id, self.partner)
        self.assertEqual(sorted(orders[0].order_line.mapped('product_uom_qty')), [2.0, 3.0])
        # same product twice in one SO is merged into one line
        self.assertEqual(len(orders[1].order_line), 1)
        self.assertEqual(orders[1].order_line.product_uom_qty, 6.0)
        self.assertEqual(orders[1].order_line.price_unit, 10.0)
        self.assertEqual(orders[0].note and 'ghi chú' in orders[0].note, True)

    def test_unknown_product_code_is_reported_with_the_code(self):
        with self.assertRaisesRegex(ValidationError, 'NOPE'):
            self._import([['1', 'KH001', 'PO-1', None, None, None, 'NOPE', None, 2]])

    def test_unknown_partner_code_is_reported_with_the_code(self):
        with self.assertRaisesRegex(ValidationError, 'KHXXX'):
            self._import([['1', 'KHXXX', 'PO-1', None, None, None, 'SP001', None, 2]])

    def test_wrong_extension_is_rejected(self):
        record = self.env['sale.order.import'].create({
            'name': 'csv', 'import_type': 'excel', 'file_name': 'orders.csv', 'file_upload': xlsx_b64([]),
        })
        with self.assertRaises(UserError):
            record.action_import_SO_excel()

    def test_cancel_removes_draft_orders_and_allows_back_to_draft(self):
        record = self._import([['1', 'KH001', 'PO-1', None, None, None, 'SP001', None, 2]])
        record.action_confirm()
        orders = record.sale_order_ids
        with self.assertRaises(ValidationError):
            record.unlink()

        record.action_cancel()

        self.assertFalse(orders.exists())
        self.assertEqual(record.state, 'cancel')
        self.assertFalse(record.line_ids)
        record.action_back_to_draft()
        self.assertEqual(record.state, 'draft')

    def test_so_count_is_computed_per_record(self):
        confirmed = self._import([['1', 'KH001', 'PO-1', None, None, None, 'SP001', None, 2]])
        confirmed.action_confirm()
        empty = self.env['sale.order.import'].create({'name': 'empty', 'import_type': 'excel'})
        self.assertEqual((confirmed | empty).mapped('so_count'), [1, 0])
