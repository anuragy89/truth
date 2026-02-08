from aiogram import types
from database import questions, groups, check_cooldown, add_xp
from keyboards import tnd_kb
from config import COOLDOWN_SECONDS, TRUTH_XP, DARE_XP

BAD_WORDS = ["sex", "nude", "xxx", "porn"]

async def auto_moderate(message: types.Message):
    text = message.text.lower()
    for word in BAD_WORDS:
        if word in text:
            try:
                await message.delete()
            except: pass
            return True
    return False

async def tnd_command(message: types.Message):
    if await auto_moderate(message):
        return

    if not check_cooldown(message.from_user.id, message.chat.id, COOLDOWN_SECONDS):
        await message.reply("⏳ Wait a few seconds before playing again 😄")
        return

    await message.reply(
        "🎲 Truth or Dare 💞\nChoose your fun 👇",
        reply_markup=tnd_kb()
    )

async def send_question(callback: types.CallbackQuery, qtype: str):
    group_mode = "family"
    grp = groups.find_one({"group_id": callback.message.chat.id})
    if grp and grp.get("flirty"):
        group_mode = "flirty"

    q = questions.aggregate([
        {"$match": {"type": qtype, "mode": group_mode, "active": True, "used_by": {"$ne": callback.from_user.id}}},
        {"$sample": {"size": 1}}
    ])
    q = list(q)
    if not q:
        q = list(questions.aggregate([
            {"$match": {"type": qtype, "mode": group_mode, "active": True}},
            {"$sample": {"size": 1}}
        ]))
    question = q[0]
    questions.update_one({"_id": question["_id"]}, {"$addToSet": {"used_by": callback.from_user.id}})

    xp = TRUTH_XP if qtype=="truth" else DARE_XP
    leveled_up = add_xp(callback.from_user.id, callback.message.chat.id, xp)

    text = f"{'🟢 TRUTH' if qtype=='truth' else '🔴 DARE'} 💖\n\n{question['text']}"
    if leveled_up:
        text += "\n\n🎉 Congrats! You leveled up 🌟"

    await callback.message.edit_text(text)
