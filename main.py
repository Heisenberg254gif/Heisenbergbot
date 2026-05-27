import asyncio
import html
import logging
import re
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, GOOGLE_API_KEY


SYSTEM_INSTRUCTION = (
    "Ты — Уолтер Уайт (Хайзенберг) из сериала Breaking Bad. Ты гениальный химик, "
    "прагматичный, немного суровый, уверенный в себе и ироничный. Отвечай на вопросы "
    "пользователей строго по делу, используя свои реальные знания, но сохраняй легкий, "
    "узнаваемый характер и стиль речи Хайзенберга. Будь лаконичен, не читай нотаций, "
    "если тебя не злят"
)

MODEL = "gemini-1.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
)

# Matches:
#   "Хайзенберг, ...", "Хайзенберг ...", any case, allows extra spaces.
TRIGGER_RE = re.compile(r"^\s*хайзенберг(?:\s*,\s*|\s+)(?P<prompt>.*)$", re.IGNORECASE)


async def generate_answer(prompt: str) -> str:
    def _sync_call() -> str:
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.8,
            },
        }
        response = requests.post(
            GEMINI_URL,
            params={"key": GOOGLE_API_KEY},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates") or []
        if not candidates:
            return ""

        parts = ((candidates[0].get("content") or {}).get("parts")) or []
        chunks = [part.get("text", "") for part in parts if isinstance(part, dict)]
        return "".join(chunks).strip()

    return await asyncio.to_thread(_sync_call)


async def on_startup() -> None:
    logging.info("Bot started.")


dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: Message) -> None:
    await message.reply(
        "Я работаю в супергруппах. Обращайся: «Хайзенберг, ...»",
        parse_mode=ParseMode.HTML,
    )


@dp.message(F.chat.type == ChatType.SUPERGROUP, F.text)
async def handle_group_message(message: Message) -> None:
    text = message.text or ""
    m = TRIGGER_RE.match(text)
    if not m:
        return

    prompt = (m.group("prompt") or "").strip()
    if not prompt:
        await message.reply("Скажи конкретно, что тебе нужно.", parse_mode=ParseMode.HTML)
        return

    try:
        answer = await generate_answer(prompt)
    except Exception:
        logging.exception("GenAI request failed")
        await message.reply("Сейчас не в духе. Попробуй позже.", parse_mode=ParseMode.HTML)
        return

    if not answer:
        await message.reply("Нечего добавить.", parse_mode=ParseMode.HTML)
        return

    await message.reply(html.escape(answer))


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Bot(token=BOT_TOKEN)
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

