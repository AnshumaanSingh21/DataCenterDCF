from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader
)


def load_all_documents():

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    knowledge_base = (
        project_root
        / "knowledge_base"
    )

    print(
        f"\nSearching in:\n{knowledge_base}"
    )

    documents = []

    pdf_files = list(
        knowledge_base.rglob("*.pdf")
    )

    print(
        f"\nFound {len(pdf_files)} PDF files"
    )

    for pdf_file in pdf_files:

        print(
            f"Loading: {pdf_file.name}"
        )

        try:

            loader = PyPDFLoader(
                str(pdf_file)
            )

            docs = loader.load()

            for doc in docs:

                doc.metadata[
                    "source_file"
                ] = pdf_file.name

            documents.extend(
                docs
            )

        except Exception as e:

            print(
                f"FAILED: {pdf_file.name}"
            )

            print(e)

    return documents