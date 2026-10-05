from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. Определение URL базы данных. Файл sql_app.db создастся автоматически в корне проекта.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Создание движка. Аргумент 'check_same_thread=False' обязателен для SQLite в FastAPI, 
# так как FastAPI может обрабатывать запросы в нескольких потоках.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Настройка фабрики сессий и базового класса для моделей
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 5. Инициализация (создание таблиц в файле DB).
# Этот вызов проверяет наличие таблиц и создает их, если их еще нет.
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
