import json
from datetime import datetime, timedelta, UTC
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8144159666:AAF7yqmPMxKs6Ho1FbIIGB0Pqe3-T5isBUY"
ALLOWED_USERS = [1296457237, 7660312786]
FILE = "keys.json"

def load_keys():
    try:
        with open(FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(FILE, 'w') as f:
        json.dump(keys, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("Привет! Я бот для управления ключами. Команды: /create_key <days>, /list_keys, /extend_key <key> <days>, /deactivate <key>, /activate <key>")

async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ALLOWED_USERS:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /create_key <days>")
        return
    try:
        days = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Days must be integer.")
        return
    keys = load_keys()
    key = str(uuid.uuid4())
    expiry_dt = datetime.now(UTC) + timedelta(days=days)
    expiry = expiry_dt.replace(microsecond=0, tzinfo=None).isoformat(timespec='seconds') + 'Z'
    keys[key] = {"device_id": "", "expiry_date": expiry}
    save_keys(keys)
    await update.message.reply_text(f"Created key: {key} with expiry {expiry}")

async def list_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ALLOWED_USERS:
        return
    keys = load_keys()
    if not keys:
        await update.message.reply_text("No keys.")
        return
    msg = ""
    for k, v in keys.items():
        msg += f"Key: {k}\nDevice ID: {v['device_id']}\nExpiry: {v['expiry_date']}\n\n"
    await update.message.reply_text(msg)

async def extend_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ALLOWED_USERS:
        return
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /extend_key <key> <days>")
        return
    key = context.args[0]
    try:
        days = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Days must be integer.")
        return
    keys = load_keys()
    if key not in keys:
        await update.message.reply_text("Key not found.")
        return
    exp_str = keys[key]['expiry_date']
    try:
        if '+' in exp_str[:-1]:
            parse_str = exp_str[:-1]
        else:
            parse_str = exp_str[:-1] + '+00:00'
        exp = datetime.fromisoformat(parse_str)
    except ValueError:
        await update.message.reply_text("Invalid expiry format.")
        return
    new_exp_dt = exp + timedelta(days=days)
    new_exp = new_exp_dt.replace(microsecond=0, tzinfo=None).isoformat(timespec='seconds') + 'Z'
    keys[key]['expiry_date'] = new_exp
    save_keys(keys)
    await update.message.reply_text(f"Extended {key} to {new_exp}")

async def deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ALLOWED_USERS:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /deactivate <key>")
        return
    key = context.args[0]
    keys = load_keys()
    if key not in keys:
        await update.message.reply_text("Key not found.")
        return
    keys[key]['expiry_date'] = "1970-01-01T00:00:00Z"
    save_keys(keys)
    await update.message.reply_text(f"Deactivated {key}")

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ALLOWED_USERS:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /activate <key>")
        return
    key = context.args[0]
    keys = load_keys()
    if key not in keys:
        await update.message.reply_text("Key not found.")
        return
    keys[key]['expiry_date'] = "2025-12-31T23:59:59Z"
    save_keys(keys)
    await update.message.reply_text(f"Activated {key} with expiry 2025-12-31T23:59:59Z")

def main():
    # Увеличиваем все таймауты для стабильной работы
    app = Application.builder().token(TOKEN)\
        .connect_timeout(30)\
        .read_timeout(30)\
        .write_timeout(30)\
        .pool_timeout(30)\
        .get_updates_connect_timeout(60)\
        .get_updates_read_timeout(60)\
        .get_updates_write_timeout(60)\
        .get_updates_pool_timeout(60)\
        .build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_key", create_key))
    app.add_handler(CommandHandler("list_keys", list_keys))
    app.add_handler(CommandHandler("extend_key", extend_key))
    app.add_handler(CommandHandler("deactivate", deactivate))
    app.add_handler(CommandHandler("activate", activate))
    
    # Запускаем с увеличенным таймаутом для long polling
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
