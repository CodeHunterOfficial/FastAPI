from fastapi import FastAPI, Depends, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from fastapi.openapi.utils import get_openapi
from database import *
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.openapi.docs import get_swagger_ui_html

from database import Base

# создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()

# определяем зависимость
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def main():
    return FileResponse("public/index.html")

@app.get("/api/users", tags=["users"])
def get_people(db: Session = Depends(get_db)):
    """
    Получение списка пользователей.
    """
    return db.query(Person).all()

@app.get("/api/users/{id}", tags=["users"])
def get_person(id, db: Session = Depends(get_db)):
    """
    Получение информации о пользователе по ID.
    """
    person = db.query(Person).filter(Person.id == id).first()
    if person is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    return person

@app.post("/api/users", tags=["users"])
def create_person(data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Создание нового пользователя.
    """
    person = Person(name=data["name"], age=data["age"])
    db.add(person)
    db.commit()
    db.refresh(person)
    return person

@app.put("/api/users", tags=["users"])
def edit_person(data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Редактирование информации о пользователе.
    """
    person = db.query(Person).filter(Person.id == data["id"]).first()
    if person is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    
    person.age = data["age"]
    person.name = data["name"]
    db.commit()
    db.refresh(person)
    return person

@app.delete("/api/users/{id}", tags=["users"])
def delete_person(id, db: Session = Depends(get_db)):
    """
    Удаление пользователя по ID.
    """
    person = db.query(Person).filter(Person.id == id).first()
    
    if person is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    
    db.delete(person)
    db.commit()
    return person

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return app.openapi()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
