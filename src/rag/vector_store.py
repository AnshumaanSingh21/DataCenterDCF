from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_vector_store(chunks):

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store


def save_vector_store(vector_store):

    vector_store.save_local(
        "knowledge_base/vector_store"
    )


def load_vector_store():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    return FAISS.load_local(
        "knowledge_base/vector_store",
        embeddings,
        allow_dangerous_deserialization=True
    )