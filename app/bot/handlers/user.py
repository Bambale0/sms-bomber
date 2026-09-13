from __future__ import annotations

import re

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.services.engine import RequestEngine

router = Router(name=__name__)
PHONE_LIKE_TEST_ID = re.compile(r"^7\d{10}$")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет. Этот бот предназначен только для разрешённого тестирования allowlisted API. "
        "Отправь тестовый идентификатор в формате 79991112233."
    )


@router.message()
async def handle_identifier(
    message: Message,
    request_engine: RequestEngine | None = None,
) -> None:
    value = (message.text or "").strip()
    if not PHONE_LIKE_TEST_ID.fullmatch(value):
        await message.answer("Нужны 11 цифр в формате 79991112233.")
        return

    if request_engine is None:
        await message.answer("Сервис временно недоступен: движок не инициализирован.")
        return

    status_message = await message.answer("Запускаю разрешённую тестовую проверку…")
    result = await request_engine.run(value)

    await status_message.edit_text(
        "Проверка завершена. "
        f"Успешно: {result.success_count}; ошибок: {result.failure_count}; "
        f"request_id: {result.request_id}."
    )
