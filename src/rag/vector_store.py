import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_HERE = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH = os.path.join(_HERE, "..", "..", "knowledge_base", "vector_store")


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

    vector_store.save_local(VECTOR_STORE_PATH)


def load_vector_store():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )