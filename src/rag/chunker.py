# NOTE: not part of the live application. Nothing in the running app
# (src/api/main.py) imports this module. The live market-intelligence path is
# src/agents/market_agent.py -> src/llm/prompts.py -> src/extraction/validator.py.
# This RAG module is unwired scaffolding — kept for reference, not executed.

from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(documents):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    return chunks