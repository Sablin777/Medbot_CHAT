from flask import Flask, render_template, jsonify, request
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os

app = Flask(__name__)



load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY


embedding = download_embeddings()
index_name = "medbot-chat"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding= embedding
)




retriever = docsearch.as_retriever(search_type = "similarity", search_kwargs = {"k":3})
system_prompt = ("""
Вы — медицинский ассистент. 
Используйте ТОЛЬКО предоставленный контекст для ответа на вопрос.

Если в контексте НЕТ информации о заболевании, о котором спрашивает пользователь, 
НЕ придумывайте ответ и напиши "В данной документации нет информации по Вашему вопросу""

Контекст: {context}
Вопрос: {input}
""")


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), # Ключ из .env
    base_url="https://openrouter.ai/api/v1", # ВАЖНО: Меняем адрес на OpenRouter
    model="openai/gpt-oss-20b:free",     # Выбранная бесплатная модель
    temperature=0.1,                        # Настройка креативности
    max_tokens=1024,
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)




@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form.get("msg")
    if not msg:
        return jsonify({"error": "Сообщение не может быть пустым"}), 400
    
    print(f"Получено сообщение: {msg}")
    
    # Оборачиваем в блок try-except для ловли ошибок
    try:
        response = rag_chain.invoke({"input": msg})
        answer = response["answer"]
        print(f"Ответ бота: {answer}")
        return str(answer)
    except Exception as e:
        # Если произошла любая ошибка, возвращаем понятный текст
        print(f"ОШИБКА: {e}")
        return "Извините, произошла ошибка на сервере. Попробуйте позже или задайте другой вопрос."


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)