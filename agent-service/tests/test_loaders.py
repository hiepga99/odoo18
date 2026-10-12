from __future__ import annotations

import unittest
from pathlib import Path

from rag.loaders import discover_documents, load_document, load_document_bytes


class LoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_dir = Path(__file__).resolve().parents[1]
        cls.data_dir = cls.base_dir / "data" / "raw"

    def test_discovers_four_demo_pdfs(self) -> None:
        documents = discover_documents(self.data_dir)
        demo_pdfs = [path for path in documents if path.suffix.lower() == ".pdf"]
        self.assertGreaterEqual(len(demo_pdfs), 4)

    def test_pdf_loader_preserves_page_number(self) -> None:
        path = self.data_dir / "coolmate_demo" / "01_coolmate_chinh_sach_doi_tra_tom_tat.pdf"
        units = load_document(path, self.data_dir)
        self.assertEqual(len(units), 2)
        self.assertEqual(units[0].page, 1)
        self.assertIn("Chính sách đổi trả", units[0].text)

    def test_loads_odoo_attachment_bytes_with_metadata(self) -> None:
        units = load_document_bytes(
            "Quy trình kiểm kê kho".encode("utf-8"),
            "quy_trinh.md",
            source_path="odoo://documents.document/42",
            metadata={"odoo_document_id": 42, "company_id": 1},
        )
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].source_path, "odoo://documents.document/42")
        self.assertEqual(units[0].metadata["odoo_document_id"], 42)
        self.assertEqual(units[0].metadata["company_id"], 1)


if __name__ == "__main__":
    unittest.main()
