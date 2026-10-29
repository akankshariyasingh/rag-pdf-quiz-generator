
import hashlib
import time

import chromadb

from config import CHROMA_DB_DIR, RETRIEVAL_TOP_K


# Initialize persistent ChromaDB
client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

collection = client.get_or_create_collection(
    name="rag_quiz_documents",
    metadata={"description": "PDF chunks for RAG-based quiz generation"},
)


def _make_document_id(source, page_number, chunk_index, text):
    raw = f"{source}|{page_number}|{chunk_index}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _make_source_id(source):
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]


def add_chunks(chunks: list[dict]) -> int:
    if not chunks:
        return 0

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        text = str(chunk.get("text", "")).strip()
        source = str(chunk.get("source", "")).strip()

        if not text or not source:
            continue

        page_number = int(chunk.get("page_number", 1))
        chunk_index = int(chunk.get("chunk_index", 0))

        ids.append(
            _make_document_id(source, page_number, chunk_index, text)
        )
        documents.append(text)
        metadatas.append({
            "source": source,
            "source_id": _make_source_id(source),
            "page_number": page_number,
            "chunk_index": chunk_index,
        })

    if not ids:
        return 0

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return len(ids)


def list_stored_pdfs() -> list[dict]:
    if collection.count() == 0:
        return []

    result = collection.get(include=["metadatas"])
    pdfs = {}

    for metadata in result.get("metadatas", []):
        if not metadata:
            continue

        source = metadata.get("source")
        source_id = metadata.get("source_id")

        if source:
            pdfs[source] = {
                "source": source,
                "source_id": source_id or _make_source_id(source),
            }

    return sorted(pdfs.values(), key=lambda item: item["source"].lower())


def get_collection_stats() -> dict:
    pdfs = list_stored_pdfs()

    return {
        "total_chunks": collection.count(),
        "total_pdfs": len(pdfs),
    }


def get_stored_chunks(limit: int = 5) -> list[dict]:
    if limit <= 0 or collection.count() == 0:
        return []

    result = collection.get(
        limit=limit,
        include=["documents", "metadatas"],
    )

    chunks = []

    for index, text in enumerate(result.get("documents", [])):
        metadata = result["metadatas"][index] or {}

        chunks.append({
            "text": text,
            "source": metadata.get("source", "Unknown"),
            "page_number": metadata.get("page_number", 1),
            "chunk_index": metadata.get("chunk_index", 0),
        })

    return chunks


def retrieve_relevant_chunks(
    query: str,
    source: str,
    top_k: int = RETRIEVAL_TOP_K,
) -> list[dict]:

    query = query.strip()

    if not query or not source or top_k <= 0:
        return []

    available = collection.count()

    if available == 0:
        return []

    print("\nStarting ChromaDB retrieval...")
    start_time = time.time()

    try:
        result = collection.query(
            query_texts=[query],
            n_results=min(top_k, available),
            where={"source": source},
            include=["documents", "metadatas", "distances"],
        )

    except Exception as exc:
        print(f"ChromaDB retrieval failed: {exc}")
        raise RuntimeError(
            "Could not retrieve document chunks from ChromaDB. "
            "Check the terminal for details."
        ) from exc

    elapsed = time.time() - start_time
    print(f"ChromaDB retrieval completed in {elapsed:.2f} seconds")

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    retrieved = []

    for index, text in enumerate(documents):
        metadata = metadatas[index] or {}

        retrieved.append({
            "text": text,
            "source": metadata.get("source", source),
            "page_number": metadata.get("page_number", 1),
            "chunk_index": metadata.get("chunk_index", 0),
            "distance": (
                distances[index]
                if index < len(distances)
                else None
            ),
        })

    print(f"Retrieved {len(retrieved)} chunks")
    return retrieved


def delete_pdf(source: str) -> int:
    source = source.strip()

    if not source or collection.count() == 0:
        return 0

    existing = collection.get(
        where={"source": source},
        include=["metadatas"],
    )

    ids = existing.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)
