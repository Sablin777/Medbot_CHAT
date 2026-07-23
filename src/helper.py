from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings



# Загружаем PDF файл 
def load_pdf_files(data):
    loader = DirectoryLoader(
        path=data,
        glob="**/*.pdf",        # Искать все PDF даже в подпапках
        loader_cls=PyPDFLoader  # Наименование загрузчика
    )
    documents = loader.load()
    return documents




# Фильтрация документов (убираем лишние метаданные)
def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata = {"source": src}
            )
        )
    return minimal_docs 




# Разделение документов на chanks 
def text_split(minimal_docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
    )
    texts_chunk = text_splitter.split_documents(minimal_docs)
    return texts_chunk




# Модель встраивания документов (Embedding Model)
def download_embeddings():
    """
    Download and return the HuggingFace embeddings model.
    """
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )
    return embeddings
