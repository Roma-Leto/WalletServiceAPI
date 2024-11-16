from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.settings import DATABASE_URL

# Создание объекта подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание сессии для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
