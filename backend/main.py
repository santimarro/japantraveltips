import asyncio
import logging
import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.api.routers.chat import chat_router
from app.api.routers.upload import file_upload_router
from app.settings import init_settings
from app.observability import init_observability
from app.telegram_bot import start_telegram_bot

load_dotenv()

app = FastAPI()

init_settings()
init_observability()

environment = os.getenv("ENVIRONMENT", "dev")

if environment == "dev":
    logger = logging.getLogger("uvicorn")
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def redirect_to_docs():
        return RedirectResponse(url="/docs")


def mount_static_files(directory, path):
    if os.path.exists(directory):
        app.mount(path, StaticFiles(directory=directory), name=f"{directory}-static")


mount_static_files("data", "/api/files/data")
mount_static_files("output", "/api/files/output")

app.include_router(chat_router, prefix="/api/chat")
app.include_router(file_upload_router, prefix="/api/chat/upload")


async def main():
    app_host = os.getenv("APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("APP_PORT", "8000"))
    reload = True if environment == "dev" else False

    config = uvicorn.Config(app, host=app_host, port=app_port, reload=reload)
    server = uvicorn.Server(config)

    # Start the Telegram bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_task = asyncio.create_task(start_telegram_bot(TELEGRAM_BOT_TOKEN))

    # Run the FastAPI app
    await server.serve()

    # Wait for the Telegram bot task to complete (it should run indefinitely)
    await telegram_task


if __name__ == "__main__":
    asyncio.run(main())
