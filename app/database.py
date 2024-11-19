from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the environment variables")

# Создание асинхронного объекта подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Создание сессии для работы с асинхронной базой данных
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()


# Функция получения сессии
async def get_db() -> AsyncSession:
    """Создает и закрывает сессию базы данных"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Инициализация базы данных (создание таблиц)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init():
    """Инициализация базы данных при старте приложения"""
    await init_db()


@asynccontextmanager
async def lifespan_handler(app):
    """Обработчик lifespan для инициализации и очистки базы данных"""
    await init_db()
    yield  # Ожидаем завершения работы приложения
