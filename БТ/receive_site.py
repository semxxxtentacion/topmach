from fastapi import FastAPI, Request
from bot import notify_admin  # функция отправки заявки админу

app = FastAPI()

@app.post("/receive_site")
async def receive_site(request: Request):
    data = await request.json()
    print("📥 Полученные данные:", data)  # Логируем входящий JSON

    telegram_id = data.get("telegram_id")
    site = data.get("site")
    keywords = data.get("keywords")

    # Необязательные поля
    region = data.get("region")
    audit = data.get("audit")
    keywords_selection = data.get("keywords_selection")
    google = data.get("google")
    yandex = data.get("yandex")

    if not telegram_id or not site:
        return {"status": "error", "message": "Missing required fields (telegram_id or site)"}

    await notify_admin(
        telegram_id=telegram_id,
        site=site,
        keywords=keywords,
        region=region,
        audit=audit,
        keywords_selection=keywords_selection,
        google=google,
        yandex=yandex
    )

    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
