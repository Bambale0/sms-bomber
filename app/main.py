from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.config import get_settings
from app.infrastructure.http import HttpClient
from app.infrastructure.logging import configure_logging
from app.services.engine import RequestEngine
from app.services.targets import SandboxTarget

logger = logging.getLogger(__name__)


async def main() -> None:
    configure_logging()
    settings = get_settings()

    http = HttpClient(timeout_seconds=settings.request_timeout_seconds)
    await http.start()

    target = SandboxTarget(settings.sandbox_target_url, settings.allowed_hosts)
    engine = RequestEngine(
        session=http.session,
        targets=(target,),
        max_concurrency=settings.max_concurrency,
        max_retries=settings.max_retries,
        retry_base_delay_seconds=settings.retry_base_delay_seconds,
    )

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    try:
        logger.info("bot_starting")
        await dispatcher.start_polling(bot, request_engine=engine)
    finally:
        await bot.session.close()
        await http.close()
        logger.info("bot_stopped")


if __name__ == "__main__":
    asyncio.run(main())
