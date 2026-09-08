from fastapi import FastAPI ,Depends ,HTTPException
from contextlib import asynccontextmanager
import asyncio
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, Base ,get_db
from app import models
from app.schemas import URLCreate
import secrets
import string
from app.redis_client import redis_client
from app.rate_limiter import rate_limit
from fastapi import Request

async def click_sync_worker():
    while True:
        await asyncio.sleep(30)

        db = next(get_db())

        try:
            keys = redis_client.keys("clicks:*")
            print("SYNC WORKER:", keys)

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
Base.metadata.create_all(bind=engine)

@app.post("/shorten")
def shorten_url(request:Request,url_data: URLCreate, db: Session = Depends(get_db)):
    rate_limit(request)

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

    return {
        "short_code": url.short_code,
        "original_url": url.original_url,
        "clicks": url.clicks,
        "created_at": url.created_at
    }   

@app.post("/sync/{short_code}")
def sync(short_code: str, db: Session = Depends(get_db)):
    sync_clicks(short_code, db)

    return {
        "message": "Clicks synced"
    }

@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):

    cached_url = redis_client.get(short_code)
    if cached_url:

      url = db.query(models.URL).filter(
        models.URL.short_code == short_code).first()

      if url:
        redis_client.incr(f"clicks:{short_code}")

      return RedirectResponse(url=cached_url)

    url = db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    redis_client.incr(f"clicks:{short_code}")

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

    print("SYNCING:", short_code, clicks)

    if clicks == 0:
        return

    url = db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()

    if not url:
        redis_client.incrby(redis_key, clicks)
        return

    url.clicks += clicks
    db.commit()


    
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

def generate_short_code(number):
    return encode_base62(number)