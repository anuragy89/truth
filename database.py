from pymongo import MongoClient
from config import MONGO_URI
import time

client = MongoClient(MONGO_URI)
db = client["truth_dare_bot"]

users = db.users
groups = db.groups
questions = db.questions
cooldowns = db.cooldowns
leaderboard = db.leaderboard

cooldowns.create_index("expire_at", expireAfterSeconds=0)

def check_cooldown(user_id, group_id, seconds):
    now = int(time.time())
    data = cooldowns.find_one({"user_id": user_id, "group_id": group_id})
    if data:
        return False
    cooldowns.insert_one({
        "user_id": user_id,
        "group_id": group_id,
        "expire_at": now + seconds
    })
    return True

def add_xp(user_id, group_id, xp):
    leaderboard.update_one(
        {"user_id": user_id, "group_id": group_id},
        {"$inc": {"xp": xp}, "$setOnInsert": {"level": 1, "badges": []}},
        upsert=True
    )
    user = leaderboard.find_one({"user_id": user_id, "group_id": group_id})
    level_threshold = user["level"]*50
    if user["xp"] >= level_threshold:
        leaderboard.update_one(
            {"user_id": user_id, "group_id": group_id},
            {"$inc": {"level": 1}}
        )
        return True
    return False
