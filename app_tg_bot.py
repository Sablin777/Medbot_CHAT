import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from src.chatbot import build_rag_chain, get_bot_answer

# --- Настройка логирования, чтобы видеть, что происходит в консоли ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Загрузка переменных окружения ---
load_dotenv()
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не найден TELEGRAM_BOT_TOKEN в .env файле")

# --- Собираем RAG-цепочку один раз при старте ---
logger.info("Инициализация RAG-цепочки...")
rag_chain = build_rag_chain()
logger.info("RAG-цепочка готова. Запускаю бота...")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я медицинский ассистент.\n\n"
        "Задайте вопрос о заболевании, и я постараюсь ответить, опираясь на "
        "имеющуюся у меня медицинскую документацию.\n\n"
        "Команда /help — краткая справка."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Просто напишите свой вопрос обычным сообщением — я отвечу.\n"
        "Важно: я не заменяю очную консультацию врача."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    logger.info(f"Сообщение от {chat_id}: {user_text}")

    # Показываем "печатает..." пока думаем над ответом
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    answer = get_bot_answer(rag_chain, user_text)
    await update.message.reply_text(answer)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка при обработке обновления: {context.error}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Бот запущен и слушает сообщения (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()