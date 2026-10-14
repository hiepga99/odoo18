import base64

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestDocumentUpload(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Document = cls.env["ai.rag.document"]

    def test_create_document_calculates_safe_metadata(self):
        document = self.Document.create(
            {
                "name": "Chính sách",
                "file_name": "folder\\policy.txt",
                "file_data": base64.b64encode(b"hello"),
            }
        )
        self.assertEqual(document.file_name, "policy.txt")
        self.assertEqual(document.file_size, 5)
        self.assertEqual(len(document.content_checksum), 64)
        self.assertFalse(document.file_is_pdf)

        pdf_document = self.Document.create(
            {
                "name": "PDF",
                "file_name": "preview.pdf",
                "file_data": base64.b64encode(b"%PDF-demo"),
            }
        )
        self.assertTrue(pdf_document.file_is_pdf)

    def test_rejects_unsupported_extension(self):
        with self.assertRaises(ValidationError):
            self.Document.create(
                {
                    "name": "Executable",
                    "file_name": "unsafe.exe",
                    "file_data": base64.b64encode(b"no"),
                }
            )

    def test_wizard_presenter_uploads_many_and_returns_document_action(self):
        wizard = self.env["ai.document.multi.upload.wizard"].create({})
        first = self.env["ir.attachment"].create(
            {
                "name": "first.txt",
                "datas": base64.b64encode(b"first"),
                "res_model": wizard._name,
                "res_id": wizard.id,
            }
        )
        second = self.env["ir.attachment"].create(
            {
                "name": "second.md",
                "datas": base64.b64encode(b"second"),
                "res_model": wizard._name,
                "res_id": wizard.id,
            }
        )
        wizard.attachment_ids = first | second

        action = wizard.action_upload_documents()

        created_ids = action["domain"][0][2]
        self.assertEqual(len(created_ids), 2)
        self.assertEqual(action["res_model"], "ai.rag.document")
        self.assertEqual(
            set(self.Document.browse(created_ids).mapped("file_name")),
            {"first.txt", "second.md"},
        )
        self.assertFalse((first | second).exists())
