import json
import os

DB_FILE = "users_db.json"


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id):
    db = load_db()
    return db.get(str(user_id), {
        "font": "bold",
        "prefix": "𓄂 ‌",
        "suffix": " ♡𝑫𝑶𝑳𝑭𓆃",
        "paid": False,
    })


def set_user(user_id, data):
    db = load_db()
    db[str(user_id)] = data
    save_db(db)
