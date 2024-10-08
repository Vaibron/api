from celery import Celery
from celery.schedules import crontab
import os
from PIL import Image
import pytesseract
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Document, DocumentText

# Создаем объект Celery
app = Celery('tasks', broker=os.environ.get("BROKER_URL"))

# Подключаемся к базе данных
engine = create_engine(os.environ.get("DATABASE_URL"))
Session = sessionmaker(bind=engine)

@app.task
def analyze_document(doc_id):
    """Извлекает текст из документа и сохраняет его в БД."""

    session = Session()

    # Загружаем документ из БД
    document = session.query(Document).filter_by(id=doc_id).first()

    if document:
        # Извлекаем текст
        image = Image.open(document.path)
        text = pytesseract.image_to_string(image)

        # Сохраняем текст в БД
        document_text = DocumentText(id_doc=doc_id, text=text)
        session.add(document_text)
        session.commit()
    else:
        print(f"Документ с ID {doc_id} не найден.")

    session.close()
