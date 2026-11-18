"""
ingest.py - read the PDFs, cut them into chunks, embed them, store them.

Run:  uv run python ingest.py
It deletes and rebuilds the collection every time, so you never get duplicates.
"""
import re
import time
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pypdf import PdfReader

import config


def load_pages(pdf_path: Path) -> list[dict]:
    """One dict per PDF page, so every chunk can say which page it came from."""
    reader = PdfReader(str(pdf_path))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        if config.EXTRACTION_MODE == "layout":
            text = page.extract_text(extraction_mode="layout")
        else:
            text = page.extract_text()
        # Collapse runs of spaces/newlines. Table rows stay on one line in "plain" mode.
        text = re.sub(r"\s+", " ", text or "").strip()
        if text:
            pages.append({"source": pdf_path.name, "page": number, "text": text})
    return pages


def chunk_pages(pages: list[dict]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = []
    for page in pages:
        for index, piece in enumerate(splitter.split_text(page["text"])):
            chunks.append({
                # Stable ID: same input gives the same ID, no random duplicates.
                "id": f"{page['source']}-p{page['page']}-c{index}",
                "text": piece,
                "source": page["source"],
                "page": page["page"],
            })
    return chunks


def embed_texts(client: OpenAI, texts: list[str], batch_size: int = 32) -> list[list[float]]:
    vectors = []
    for start in range(0, len(texts), batch_size):
        batch = [config.DOC_PREFIX + t for t in texts[start:start + batch_size]]
        response = client.embeddings.create(model=config.EMBEDDING_MODEL, input=batch)
        vectors.extend(item.embedding for item in response.data)
    return vectors


def main() -> None:
    started = time.time()
    pdfs = sorted(Path(config.DOCUMENTS_DIR).glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {config.DOCUMENTS_DIR}/")

    pages = []
    for pdf in pdfs:
        got = load_pages(pdf)
        print(f"{pdf.name}: {len(got)} pages with text")
        pages.extend(got)

    chunks = chunk_pages(pages)
    sizes = [len(c["text"]) for c in chunks]
    print(f"{len(chunks)} chunks (size {config.CHUNK_SIZE} / overlap {config.CHUNK_OVERLAP} characters); "
          f"shortest {min(sizes)}, longest {max(sizes)}, average {sum(sizes) // len(sizes)} characters")

    embed_client = OpenAI(base_url=config.EMBEDDING_BASE_URL, api_key=config.EMBEDDING_API_KEY)
    vectors = embed_texts(embed_client, [c["text"] for c in chunks])
    print(f"Embedded with {config.EMBEDDING_MODEL}, {len(vectors[0])} dimensions")

    db = chromadb.PersistentClient(path=config.CHROMA_DIR)
    try:
        db.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass  # first run: nothing to delete
    collection = db.create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # so 1 - distance is a real similarity
    )
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=vectors,
        metadatas=[{"source": c["source"], "page": c["page"]} for c in chunks],
    )
    print(f"Stored {collection.count()} chunks in {config.CHROMA_DIR}/ in {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
