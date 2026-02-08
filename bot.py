from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config import BOT_TOKEN, WEBHOOK_URL, OWNER_ID
from keyboards import start_kb
from handlers import tnd_command, send_question
from database import users, groups

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    users.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"user_id": message.from_user.id}},
        upsert=True
    )
    await message.answer(
        "💖 Welcome to Truth & Dare Bot!\n🎲 Fun • Romantic • Safe\n👥 Best in groups\nTap below to start 👇",
        reply_markup=start_kb()
    )

@dp.message_handler(commands=["tnd"], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def tnd(message: types.Message):
    groups.update_one(
        {"group_id": message.chat.id},
        {"$setOnInsert": {"group_id": message.chat.id, "flirty": False}},
        upsert=True
    )
    await tnd_command(message)

@dp.callback_query_handler(lambda c: c.data in ["truth", "dare"])
async def callbacks(call: types.CallbackQuery):
    await send_question(call, call.data)

@dp.message_handler(commands=["flirty_on"])
async def flirty_on(message: types.Message):
    admins = [a.user.id for a in await message.chat.get_administrators()]
    if message.from_user.id != OWNER_ID and message.from_user.id not in admins:
        return
    groups.update_one({"group_id": message.chat.id}, {"$set": {"flirty": True}})
    await message.reply("💞 Flirty mode enabled! Safe & fun 🌸")

@dp.message_handler(commands=["broadcast"])
async def broadcast(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    text = message.text.replace("/broadcast", "").strip()
    for u in users.find():
        try: await bot.send_message(u["user_id"], text)
        except: pass
    for g in groups.find():
        try: await bot.send_message(g["group_id"], text)
        except: pass
    await message.reply("✅ Broadcast sent!")

if __name__ == "__main__":
    executor.start_webhook(
        dispatcher=dp,
        webhook_path="/",
        on_startup=lambda _: bot.set_webhook(WEBHOOK_URL),
        skip_updates=True,
        host="0.0.0.0",
        port=8000
    )
