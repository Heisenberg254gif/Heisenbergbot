import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from google import genai
from google.genai import types

from config import BOT_TOKEN, GOOGLE_API_KEY


SYSTEM_INSTRUCTION = (
    "Ты — Уолтер Уайт (Хайзенберг) из сериала Breaking Bad. Ты гениальный химик, "
    "прагматичный, немного суровый, уверенный в себе и ироничный. Отвечай на вопросы "
    "пользователей строго по делу, используя свои реальные знания, но сохраняй легкий, "
    "узнаваемый характер и стиль речи Хайзенберга. Будь лаконичен, не читай нотаций, "
    "если тебя не злят"
)

MODEL = "gemini-1.5-flash"

# Matches:
#   "Хайзенберг, ...", "Хайзенберг ...", any case, allows extra spaces.
TRIGGER_RE = re.compile(r"^\s*хайзенберг(?:\s*,\s*|\s+)(?P<prompt>.*)$", re.IGNORECASE)


genai_client = genai.Client(api_key=GOOGLE_API_KEY)


async def generate_answer(prompt: str) -> str:
    def _sync_call() -> str:
        resp = genai_client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        return (resp.text or "").strip()

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

    await message.reply(answer, parse_mode=ParseMode.HTML)


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

