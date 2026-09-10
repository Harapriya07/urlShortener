from fastapi import FastAPI ,Depends ,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import engine, Base ,get_db
from app import models
from app.schemas import URLCreate
from app.redis_client import redis_client
from app.rate_limiter import rate_limit
from fastapi import Request
from datetime import date , timedelta
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

async def click_sync_worker():
    while True:
        await asyncio.sleep(30)

        db = next(get_db())

        try:
            keys = list( redis_client.scan_iter(match="clicks:*") )

            for key in keys:
                short_code = key.split(":", 1)[1]
                sync_clicks(short_code, db)      
        finally:
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(click_sync_worker())

    yield

    task.cancel()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/shorten")
def shorten_url(request:Request,url_data: URLCreate, db: Session = Depends(get_db)):
    rate_limit(request)

    existing_url = db.query(models.URL).filter(
    models.URL.original_url == str(url_data.url)
    ).first()

    if existing_url:
      return {
        "short_code": existing_url.short_code
    }

    new_url = models.URL(
        original_url=str(url_data.url)
    )

    db.add(new_url)
    db.flush()
    
    short_code=encode_base62(new_url.id)

    new_url.short_code=short_code
    db.commit()
    db.refresh(new_url)
    return {
        "short_code": new_url.short_code
    }

@app.get("/analytics/{short_code}")
def get_analytics(short_code: str, db: Session = Depends(get_db)):

    url = db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    today = date.today().isoformat()
    today_clicks = redis_client.get(
    f"daily_clicks:{short_code}:{today}")

    daily_clicks = {}

    for i in range(7):
      day = date.today() - timedelta(days=i)
      key = f"daily_clicks:{short_code}:{day.isoformat()}"

      clicks = redis_client.get(key)

      daily_clicks[day.isoformat()] = int(clicks or 0)

    return {
        "short_code": url.short_code,
        "original_url": url.original_url,
        "clicks": url.clicks,
        "today_clicks": int(today_clicks or 0),
        "daily_clicks": daily_clicks,
        "created_at": url.created_at
    }   


@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):

    cached_url = redis_client.get(short_code)
    if cached_url:

      url = db.query(models.URL).filter(
        models.URL.short_code == short_code).first()

      if url:
        today = date.today().isoformat()
        redis_client.incr(f"clicks:{short_code}")
        daily_key=(f"daily_clicks:{short_code}:{today}")

        redis_client.incr(daily_key)
        redis_client.expire(daily_key, 60 * 60 * 24 * 30)

      return RedirectResponse(url=cached_url)

    url = db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    today = date.today().isoformat()
    redis_client.incr(f"clicks:{short_code}")
    daily_key=(f"daily_clicks:{short_code}:{today}")

    redis_client.incr(daily_key)
    redis_client.expire(daily_key, 60 * 60 * 24 * 30)

    redis_client.setex(short_code,3600, url.original_url)

    return RedirectResponse(url=url.original_url)


def sync_clicks(short_code: str, db: Session):
    redis_key = f"clicks:{short_code}"

    script = """
    local clicks = redis.call('GET', KEYS[1])

    if clicks == false then
        return 0
    end

    redis.call('SET', KEYS[1], 0)

    return tonumber(clicks)
    """

    clicks = redis_client.eval(script, 1, redis_key)

    if clicks == 0:
        return

    try:
        url = db.query(models.URL).filter(
            models.URL.short_code == short_code
        ).first()

        if not url:
            redis_client.incrby(redis_key, clicks)
            return

        url.clicks += clicks
        db.commit()

        logger.info("SYNC COMPLETE: %s %s", short_code, clicks)

    except Exception as e:
        db.rollback()
        redis_client.incrby(redis_key, clicks)
        logger.error("SYNC FAILED: %s %s", short_code, e)

    
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(number):
    if number == 0:
        return BASE62[0]

    result = ""

    while number > 0:
        remainder = number % 62
        result = BASE62[remainder] + result
        number = number // 62

    return result
