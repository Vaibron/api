# 1. Запуск веб-сервера:

uvicorn main:app --reload

# 2. Проверка работы API:

Загрузка документа:

Отправьте POST-запрос на http://localhost:8000/upload_doc с файлом в формате изображения и датой документа.
Получите ID загруженного документа в ответе.

Удаление документа:

Отправьте DELETE-запрос на http://localhost:8000/doc_delete/<id_документа>.
Проверьте, что документ был удален с диска и из базы данных.

Анализ документа:

Отправьте POST-запрос на http://localhost:8000/doc_analyse/<id_документа>.
Проверьте, что задача Celery была запущена для анализа документа.

Получение текста:

Отправьте GET-запрос на http://localhost:8000/get_text/<id_документа>.
Получите текст из документа в ответе.

# 3. Настройка RabbitMQ:

Установите RabbitMQ: https://www.rabbitmq.com/

Запустите RabbitMQ.

Убедитесь, что в файле config.py установлена правильная URL для подключения к брокеру.

# 4. Настройка Tesseract:

Установите Tesseract: https://tesseract-ocr.github.io/

Убедитесь, что в системе установлены языковые пакеты для Tesseract.

Проверьте, что путь к Tesseract установлен в переменной окружения TESSDATA_PREFIX.


# Важно:

Замените значения в файле config.py на свои собственные.
Убедитесь, что в системе установлены все необходимые зависимости.
Настройте RabbitMQ и Tesseract в соответствии с вашим окружением.
Этот код предоставляет базовый пример. Вы можете его модифицировать и дополнить в соответствии с вашими потребностями.


#
#
# Swagger Documentation, Dockerfile & docker-compose
Вот обновленный код с Swagger документацией, Dockerfile и docker-compose:

1. main.py:
```python
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
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

app = FastAPI(
    title="Document Processing API",
    description="API for document uploading, deletion, and analysis.",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

Подключаемся к базе данных
engine = create_engine(config.DATABASE_URL)
Session = sessionmaker(bind=engine)

Подключаемся к Celery
app.celery_app = Celery('tasks', broker=config.BROKER_URL)

@app.on_event("startup")
async def startup_event():
    """Подключаем брокер Celery."""
    app.celery_app.conf.broker_url = config.BROKER_URL

@app.post("/upload_doc", summary="Загрузка документа", description="Загружает документ, сохраняет его на диск и добавляет запись в БД.")
async def upload_document(file: UploadFile = File(...), date: datetime.date = Form(...)):
    """Загружает документ, сохраняет его на диск и добавляет запись в БД."""
    # ... (остальной код без изменений)

@app.delete("/doc_delete/{doc_id}", summary="Удаление документа", description="Удаляет документ из базы данных и с диска.")
async def delete_document(doc_id: int):
    """Удаляет документ из базы данных и с диска."""
    # ... (остальной код без изменений)

@app.post("/doc_analyse/{doc_id}", summary="Анализ документа", description="Инициализирует задачу Celery для анализа документа.")
async def analyze_document(doc_id: int):
    """Инициализирует задачу Celery для анализа документа."""
    # ... (остальной код без изменений)

@app.get("/get_text/{doc_id}", summary="Получение текста", description="Возвращает текст из БД по ID документа.")
async def get_text(doc_id: int):
    """Возвращает текст из БД по ID документа."""
    # ... (остальной код без изменений)

def custom_openapi():
    """Custom OpenAPI schema for Swagger documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Document Processing API",
        version="1.0.0",
        description="API for document uploading, deletion, and analysis.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/docs", include_in_schema=False)
async def get_documentation():
    """Returns Swagger UI HTML."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Document Processing API",
    )

@app.get("/redoc", include_in_schema=False)
async def get_redoc_html():
    """Returns ReDoc HTML."""
    return get_swagger_ui_oauth2_redirect_html()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. Dockerfile:

```
FROM python:3.9
```

Устанавливаем зависимости
```
COPY requirements.txt .
RUN pip install -r requirements.txt
```

Копируем файлы приложения
```
COPY . .
```

Устанавливаем tesseract
```
RUN apt-get update && apt-get install -y tesseract-ocr
```

Устанавливаем языковой пакет tesseract
```
RUN apt-get update && apt-get install -y tesseract-ocr-eng
```

Устанавливаем RabbitMQ
```
RUN apt-get update && apt-get install -y rabbitmq-server
```

Запускаем RabbitMQ
```
RUN rabbitmq-server -detached
```

Запускаем приложение

CMD ["uvicorn", "main:app", "--reload"]

3. docker-compose.yml:
```
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - rabbitmq
    environment:
      DATABASE_URL: "postgresql://user:password@host:port/database"
      BROKER_URL: "amqp://guest:guest@rabbitmq:5672//"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
```

4. Запуск проекта:
```
docker-compose up -d
```

Запуск веб-сервера:

Откройте браузер и перейдите по адресу http://localhost:8000/docs или http://localhost:8000/redoc.
Вы увидите Swagger UI или ReDoc интерфейс с документацией API.
Вы можете использовать Swagger UI или ReDoc для тестирования API.
Важно:

Замените значения в docker-compose.yml на свои собственные.
Запустите docker-compose build для сборки Docker образа.
Запустите docker-compose up -d для запуска контейнера.
Проверьте, что RabbitMQ запущен и доступен по адресу http://localhost:15672/.
Этот код реализует веб-сервер с API для загрузки, удаления и анализа документов, используя uvicorn, базы данных PostgreSQL, библиотеку tesseract для извлечения текста и брокер сообщений RabbitMQ. Swagger документация обеспечивает удобное описание API для разработчиков. Dockerfile и docker-compose позволяют легко развернуть приложение в контейнере Docker.
