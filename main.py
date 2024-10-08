import os
import base64
import datetime
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Document, DocumentText
from celery import Celery
import config
import json

app = FastAPI()

# Подключаемся к базе данных
engine = create_engine(config.DATABASE_URL)
Session = sessionmaker(bind=engine)

# Подключаемся к Celery
app.celery_app = Celery('tasks', broker=config.BROKER_URL)

@app.on_event("startup")
async def startup_event():
    """Подключаем брокер Celery."""
    app.celery_app.conf.broker_url = config.BROKER_URL

@app.post("/upload_doc")
async def upload_document(file: UploadFile = File(...), date: datetime.date = Form(...)):
    """Загружает документ, сохраняет его на диск и добавляет запись в БД."""

    # Проверяем, что файл не пустой
    if not file.file:
        raise HTTPException(status_code=400, detail="Файл не был загружен.")

    # Сохраняем файл на диск
    file_path = os.path.join("documents", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Добавляем запись в БД
    session = Session()
    document = Document(path=file_path, date=date)
    session.add(document)
    session.commit()

    # Возвращаем ID документа
    return JSONResponse({"id": document.id})

@app.delete("/doc_delete/{doc_id}")
async def delete_document(doc_id: int):
    """Удаляет документ из базы данных и с диска."""

    session = Session()

    # Загружаем документ из БД
    document = session.query(Document).filter_by(id=doc_id).first()

    if document:
        # Удаляем документ с диска
        os.remove(document.path)

        # Удаляем документ из БД
        session.delete(document)
        session.commit()

        return JSONResponse({"message": f"Документ с ID {doc_id} успешно удален."})
    else:
        return JSONResponse({"message": f"Документ с ID {doc_id} не найден."}, status_code=404)

@app.post("/doc_analyse/{doc_id}")
async def analyze_document(doc_id: int):
    """Инициализирует задачу Celery для анализа документа."""

    # Вызываем задачу Celery
    app.celery_app.send_task("tasks.analyze_document", args=(doc_id,))

    return JSONResponse({"message": f"Анализ документа с ID {doc_id} запущен."})

@app.get("/get_text/{doc_id}")
async def get_text(doc_id: int):
    """Возвращает текст из БД по ID документа."""

    session = Session()

    # Загружаем текст из БД
    text = session.query(DocumentText).filter_by(id_doc=doc_id).first()

    if text:
        return JSONResponse({"text": text.text})
    else:
        return JSONResponse({"message": f"Текст для документа с ID {doc_id} не найден."}, status_code=404)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
