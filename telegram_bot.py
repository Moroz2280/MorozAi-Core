import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime

TOKEN = "8025765826:AAEndFJNYxlABibHUMD6MEoY0VHSNsNtBIY"
logger = logging.getLogger(__name__)

class TelegramBotManager:
    def __init__(self):
        self.app = ApplicationBuilder().token(TOKEN).build()
        self.is_running = False
        self.setup_handlers()

    # ... (весь твой код TelegramBotManager без изменений) ...