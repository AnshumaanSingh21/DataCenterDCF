# NOTE: not part of the live application. Nothing in the running app
# (src/api/main.py) imports this module. The live market-intelligence path is
# src/agents/market_agent.py -> src/llm/prompts.py -> src/extraction/validator.py.
# This RAG module is unwired scaffolding — kept for reference, not executed.

from src.rag.vector_store import load_vector_store


def retrieve(query, k=5):

    vector_store = load_vector_store()

    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


if __name__ == "__main__":

    query = input(
        "Enter query: "
    )

    results = retrieve(query)

    for i, result in enumerate(results, start=1):

        print("\n")
        print("=" * 80)

        print(
            f"Result {i}"
        )

        print(
            result.metadata
        )

        print(
            result.page_content[:1000]
        )