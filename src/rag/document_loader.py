from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader


def load_all_documents():

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    knowledge_base = project_root / "knowledge_base"

    print(f"\nSearching in:\n{knowledge_base}")

    documents = []

    # ── PDFs ─────────────────────────────────────────────────────────────────
    pdf_files = list(knowledge_base.rglob("*.pdf"))
    print(f"\nFound {len(pdf_files)} PDF files")

    for pdf_file in pdf_files:
        print(f"Loading PDF : {pdf_file.name}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = pdf_file.name
                doc.metadata["source_type"] = "pdf"
            documents.extend(docs)
        except Exception as e:
            print(f"FAILED: {pdf_file.name} — {e}")

    # ── Web content (.txt fetched via Jina Reader) ────────────────────────────
    web_dir = knowledge_base / "web_content"
    txt_files = list(web_dir.rglob("*.txt")) if web_dir.exists() else []
    print(f"\nFound {len(txt_files)} web content files")

    for txt_file in txt_files:
        print(f"Loading TXT : {txt_file.name}")
        try:
            loader = TextLoader(str(txt_file), encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = txt_file.name
                doc.metadata["source_type"] = "web"
            documents.extend(docs)
        except Exception as e:
            print(f"FAILED: {txt_file.name} — {e}")

    return documents