from __future__ import annotations

import argparse

from mcp.server import MCPServer

from ..config import settings
from ..generate import answer_from_odoo_documents
from ..retrieval import Retriever
from .rpc import OdooRpcClient


mcp = MCPServer(
    name="odoo-rag",
    instructions=(
        "Expose only the Odoo RAG document operations required by the agent. "
        "Odoo authentication and record rules remain authoritative."
    ),
)
_rpc: OdooRpcClient | None = None
_retriever: Retriever | None = None


def get_rpc() -> OdooRpcClient:
    global _rpc
    if _rpc is None:
        _rpc = OdooRpcClient()
    return _rpc


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


@mcp.tool()
def claim_pending_rag_documents(limit: int = 10) -> list[dict]:
    """Claim pending indexing or cleanup jobs from Odoo."""
    return get_rpc().call("mcp_claim_pending_documents", limit)


@mcp.tool()
def get_rag_document_payload(document_id: int) -> dict:
    """Read one Odoo attachment payload for RAG processing."""
    return get_rpc().call("mcp_get_document_payload", document_id)


@mcp.tool()
def update_rag_document_progress(document_id: int, progress: int, stage: str) -> dict:
    """Update the visible indexing progress for one document."""
    return get_rpc().call(
        "mcp_update_document_progress", document_id, progress, stage
    )


@mcp.tool()
def mark_rag_document_indexed(
    document_id: int,
    chunk_count: int,
    checksum: str,
    collection: str,
    storage_backend: str,
    storage_location: str,
    chunk_previews: list[dict],
    page_count: int = 0,
    clean_char_count: int = 0,
    chunk_size: int = 0,
    chunk_overlap: int = 0,
    embedding_model: str = "",
) -> dict:
    """Write indexing status and safe chunk previews back to Odoo."""
    return get_rpc().call(
        "mcp_mark_document_indexed",
        document_id,
        chunk_count,
        checksum,
        collection,
        storage_backend,
        storage_location,
        chunk_previews,
        page_count,
        clean_char_count,
        chunk_size,
        chunk_overlap,
        embedding_model,
    )


@mcp.tool()
def mark_rag_document_error(document_id: int, error_message: str) -> bool:
    """Record an indexing error in Odoo."""
    return bool(get_rpc().call("mcp_mark_document_error", document_id, error_message))


@mcp.tool()
def mark_rag_document_vectors_deleted(document_id: int) -> bool:
    """Confirm vector cleanup to Odoo."""
    return bool(get_rpc().call("mcp_mark_document_vectors_deleted", document_id))


@mcp.tool()
def search_internal_documents(question: str, top_k: int = 4) -> list[dict]:
    """Search only indexed documents readable by the configured Odoo API-key user."""
    scope = get_rpc().call("mcp_get_current_user_rag_scope")
    results = get_retriever().search(
        question,
        top_k=max(1, min(int(top_k), 20)),
        allowed_document_ids=scope["allowed_document_ids"],
        company_id=int(scope["company_id"]),
    )
    return [result.to_dict() for result in results]


@mcp.tool()
def answer_internal_documents(question: str, top_k: int = 4) -> dict:
    """Answer from authorized internal documents only and include citations."""
    scope = get_rpc().call("mcp_get_current_user_rag_scope")
    answer, results = answer_from_odoo_documents(
        question,
        top_k=max(1, min(int(top_k), 20)),
        allowed_document_ids=scope["allowed_document_ids"],
        company_id=int(scope["company_id"]),
        retriever=get_retriever(),
    )
    return {
        "answer": answer,
        "sources": [result.to_dict() for result in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Odoo RAG MCP server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="streamable-http",
    )
    parser.add_argument("--host", default=settings.mcp_host)
    parser.add_argument("--port", type=int, default=settings.mcp_port)
    args = parser.parse_args()
    options = {}
    if args.transport == "streamable-http":
        options = {"host": args.host, "port": args.port}
    mcp.run(transport=args.transport, **options)


if __name__ == "__main__":
    main()
