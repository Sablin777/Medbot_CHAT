# src/chatbot.py
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.helper import download_embeddings
from src.prompt import *
import os

def build_rag_chain():
    embedding = download_embeddings()
    index_name = "medbot-chat"

    docsearch = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embedding
    )
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    system_prompt = ("""
    Вы — медицинский ассистент. 
    Используйте ТОЛЬКО предоставленный контекст для ответа на вопрос.
    Если в контексте НЕТ информации о заболевании, о котором спрашивает пользователь, 
    НЕ придумывайте ответ и напиши "В данной документации нет информации по Вашему вопросу"

    Контекст: {context}
    Вопрос: {input}
    """)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    llm = ChatOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        model="openai/gpt-oss-20b:free",
        temperature=0.1,
        max_tokens=1024,
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)


def get_bot_answer(rag_chain, user_message: str) -> str:
    try:
        response = rag_chain.invoke({"input": user_message})
        return response["answer"]
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return "Извините, произошла ошибка на сервере. Попробуйте позже."