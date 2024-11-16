from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Основной класс для SQLAlchemy моделей
Base = declarative_base()

# Модель кошелька в базе данных
class Wallet(Base):
    """
    Модель кошелька, которая представляет таблицу "wallets" в базе данных.

    Параметры:
    - id (int): Идентификатор кошелька, первичный ключ.
    - uuid (str): Уникальный идентификатор кошелька.
    - balance (int): Баланс кошелька, по умолчанию равен 0.
    """
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True, index=True)  # Идентификатор кошелька
    uuid = Column(String, unique=True, index=True)  # UUID кошелька (уникальный)
    balance = Column(Integer, default=0)  # Баланс кошелька, по умолчанию 0
