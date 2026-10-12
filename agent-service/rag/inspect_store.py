from __future__ import annotations

from collections import Counter

from .vector_store import VectorStore


def main() -> None:
    store = VectorStore()
    collection = store.get_or_create_collection()
    data = collection.get(include=["metadatas", "documents"])
    document_counts = Counter(
        str(metadata.get("odoo_document_id", "local"))
        for metadata in (data.get("metadatas") or [])
    )
    print(f"Storage: {store.location}")
    print(f"Collection: {store.collection_name}")
    print(f"Total vectors: {collection.count()}")
    for document_id, count in sorted(document_counts.items()):
        print(f"- Odoo document {document_id}: {count} vectors")


if __name__ == "__main__":
    main()
