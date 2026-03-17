import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
import os
from datetime import datetime, UTC

app = FastAPI()

KEYS_FILE = "keys.json"

# Загрузка или инициализация keys.json
if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({}, f)

def load_keys() -> Dict:
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(keys: Dict):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

class AuthRequest(BaseModel):
    key: str
    device_id: str

@app.post("/api/authenticate")
async def authenticate(request: AuthRequest):
    keys = load_keys()
    if request.key not in keys:
        return {"status": "invalid", "message": "Key is already used on another device or expired"}
    
    key_data = keys[request.key]
    exp_str = key_data["expiry_date"]
    try:
        if '+' in exp_str[:-1]:
            parse_str = exp_str[:-1]
        else:
            parse_str = exp_str[:-1] + '+00:00'
        exp_dt = datetime.fromisoformat(parse_str)
        if exp_dt < datetime.now(UTC):
            return {"status": "invalid", "message": "Key is already used on another device or expired"}
    except ValueError:
        return {"status": "invalid", "message": "Key is already used on another device or expired"}
    
    if key_data["device_id"] == "":
        # Первая авторизация: записываем device_id
        key_data["device_id"] = request.device_id
        keys[request.key] = key_data
        save_keys(keys)
        return {"status": "valid", "expiry_date": key_data["expiry_date"]}
    else:
        # Повторная: проверяем совпадение
        if key_data["device_id"] == request.device_id:
            return {"status": "valid", "expiry_date": key_data["expiry_date"]}
        else:
            return {"status": "invalid", "message": "Key is already used on another device or expired"}

# Для добавления нового ключа (ручное, не через API)
def add_key(key: str, expiry_date: str = "2025-12-31T23:59:59Z"):
    keys = load_keys()
    if key not in keys:
        keys[key] = {"device_id": "", "expiry_date": expiry_date}
        save_keys(keys)