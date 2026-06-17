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