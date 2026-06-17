from pathlib import Path

from document_loader import load_all_documents
from chunker import create_chunks
from vector_store import (
    build_vector_store,
    save_vector_store
)


def main():

    print("=" * 80)
    print("BUILDING KNOWLEDGE BASE")
    print("=" * 80)

    print("\nCurrent Working Directory:")
    print(Path.cwd())

    print("\nKnowledge Base Path:")
    print(Path("knowledge_base").resolve())

    print("\nLoading documents...")

    docs = load_all_documents()

    print(f"\nDocuments loaded: {len(docs)}")

    if len(docs) == 0:

        print(
            "\nERROR: No documents loaded."
        )

        print(
            "Check knowledge_base folder path."
        )

        return

    print("\nChunking documents...")

    chunks = create_chunks(docs)

    print(
        f"Chunks created: {len(chunks)}"
    )

    if len(chunks) == 0:

        print(
            "\nERROR: No chunks created."
        )

        return

    print("\nBuilding FAISS index...")

    vector_store = build_vector_store(
        chunks
    )

    save_vector_store(
        vector_store
    )

    print(
        "\nKnowledge base built successfully!"
    )


if __name__ == "__main__":

    main()