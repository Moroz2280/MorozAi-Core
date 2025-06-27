from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio
import logging
from telegram_bot import TelegramBotManager
from aligenerator import generate_code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MorozAI Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stats = {
    "requests_today": 0,
    "successful_generations": 0,
    "errors": 0,
    "start_time": datetime.now()
}

telegram_bot = None

@app.on_event("startup")
async def startup_event():
    global telegram_bot
    logger.info("Запуск MorozAI Core...")
    telegram_bot = TelegramBotManager()
    asyncio.create_task(telegram_bot.start())
    logger.info("Telegram бот запущен")

@app.get("/")
async def home():
    uptime = datetime.now() - stats["start_time"]
    return {"msg": "MorozAI Core 🚀", "status": "active", "uptime": str(uptime)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "telegram_bot_status": "active" if telegram_bot and telegram_bot.is_running else "inactive"
    }

@app.post("/ai_gen")
async def ai_generate_code(prompt: str, background_tasks: BackgroundTasks):
    if not prompt or len(prompt.strip()) < 3:
        raise HTTPException(status_code=400, detail="Промпт слишком короткий")
    stats["requests_today"] += 1
    try:
        logger.info(f"Генерация кода для промпта: {prompt[:50]}")
        result = generate_code(prompt.strip())
        stats["successful_generations"] += 1
        if telegram_bot and telegram_bot.is_running:
            background_tasks.add_task(telegram_bot.send_generation_notification, prompt, result)
        return {"response": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Ошибка генерации: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    uptime = datetime.now() - stats["start_time"]
    success_rate = (
        (stats["successful_generations"] / max(stats["requests_today"], 1)) * 100
        if stats["requests_today"] > 0 else 0
    )
    return {
        **stats,
        "uptime": str(uptime),
        "success_rate": round(success_rate, 2),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)