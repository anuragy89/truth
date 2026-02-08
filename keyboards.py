from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import UPDATE_CHANNEL

def start_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("➕ Add me to Group 💬", url="https://t.me/YourBotUsername?startgroup=true"),
        InlineKeyboardButton("🎮 How to Use", callback_data="how"),
        InlineKeyboardButton("📖 Help", callback_data="help"),
        InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL)
    )
    return kb

def tnd_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🟢 Truth 💬", callback_data="truth"),
        InlineKeyboardButton("🔴 Dare 🎯", callback_data="dare")
    )
    return kb
