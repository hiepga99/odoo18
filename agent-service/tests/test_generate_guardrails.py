import unittest
from unittest.mock import patch

from rag.generate import NO_CONTEXT_ANSWER, answer_from_odoo_documents, answer_question
from rag.retrieval import SearchResult


class FakeRetriever:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, question, top_k, *, allowed_document_ids=None, company_id=None):
        self.calls.append(
            {
                "question": question,
                "top_k": top_k,
                "allowed_document_ids": allowed_document_ids,
                "company_id": company_id,
            }
        )
        return self.results


class GenerateGuardrailTests(unittest.TestCase):
    @patch("rag.generate.OpenAI")
    def test_low_similarity_stops_before_llm(self, openai):
        result = SearchResult(
            rank=1,
            text="Unrelated text",
            source_path="odoo://ai.rag.document/1",
            source_name="other.pdf",
            page=1,
            chunk_index=0,
            distance=0.8,
            similarity=0.2,
            odoo_document_id=1,
            company_id=2,
        )
        answer, sources = answer_question(
            "Question outside the document",
            min_similarity=0.45,
            retriever=FakeRetriever([result]),
        )
        self.assertEqual(answer, NO_CONTEXT_ANSWER)
        self.assertEqual(sources, [])
        openai.assert_not_called()

    def test_odoo_answer_requires_authorized_documents(self):
        retriever = FakeRetriever([])
        answer, sources = answer_from_odoo_documents(
            "Internal policy?",
            allowed_document_ids=[],
            company_id=1,
            retriever=retriever,
        )
        self.assertEqual(answer, NO_CONTEXT_ANSWER)
        self.assertEqual(sources, [])
        self.assertEqual(retriever.calls, [])

    @patch("rag.generate.OpenAI")
    def test_odoo_filters_are_forwarded(self, openai):
        retriever = FakeRetriever([])
        answer, _sources = answer_from_odoo_documents(
            "Internal policy?",
            allowed_document_ids=[4, 8],
            company_id=3,
            retriever=retriever,
        )
        self.assertEqual(answer, NO_CONTEXT_ANSWER)
        self.assertEqual(retriever.calls[0]["allowed_document_ids"], [4, 8])
        self.assertEqual(retriever.calls[0]["company_id"], 3)
        openai.assert_not_called()


if __name__ == "__main__":
    unittest.main()
