from fastapi import FastAPI ,Depends ,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, Base ,get_db
from app import models
from app.schemas import URLCreate
import secrets
import string
app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.post("/shorten")
def shorten_url(url_data: URLCreate, db: Session = Depends(get_db)):
    short_code = generate_short_code()

    new_url = models.URL(
        original_url=url_data.url,
        short_code=short_code
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {
        "short_code": new_url.short_code
    }

@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    url = db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=url.original_url)

@app.get("/")
def home():
    try:
        with engine.connect() as connection:
            result=connection.execute(text("SELECT 1"))
            return{
                "message": "Database connected!",
                "result": result.scalar()
            }
    except Exception as e:
        return{
            "message": "Database connection failed",
            "error": str(e)
        }    

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))    