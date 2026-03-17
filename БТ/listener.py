from flask import Flask, request
from datetime import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = "hook_log.jsonl"

@app.route('/add-click/<token>', methods=['GET', 'HEAD'])
def handle_click(token):
    # Чтение всего, что может прислать софт
    log = {
        "time": datetime.now().isoformat(),
        "method": request.method,
        "token": token,
        "remote_addr": request.remote_addr,
        "headers": dict(request.headers),
        "query_params": request.args.to_dict(),
        "raw_data": request.get_data(as_text=True),
    }

    # Печатаем в консоль
    print("=== Новый входящий запрос ===")
    print(json.dumps(log, indent=2))

    # Сохраняем в лог
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

    return "ok", 200

if __name__ == '__main__':
    os.system(f"touch {LOG_FILE}")  # создаём файл, если его нет
    app.run(host='0.0.0.0', port=80)
