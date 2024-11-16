from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.crud import process_transaction, get_balance
from app.database import engine, get_db
from app.models import Base

# Инициализация FastAPI приложения
app = FastAPI()

# Создание всех таблиц в базе данных (если они еще не существуют)
Base.metadata.create_all(bind=engine)


# Модель запроса для операций с кошельком (с помощью Pydantic)
class WalletRequest(BaseModel):
    """
    Модель, описывающая структуру запроса для выполнения операций с кошельком.
    Используется для валидации входящих данных.

    Параметры:
    - operationType (str): Тип операции (может быть "DEPOSIT" для пополнения и "WITHDRAW"
    для снятия средств).
    - amount (int): Сумма операции (положительное число для пополнения и снятия).
    """
    operationType: str  # Тип операции (DEPOSIT/WITHDRAW)
    amount: int  # Сумма операции


# Эндпоинт для создания операции с кошельком (пополнение или снятие средств)
@app.post("/api/v1/wallets/{wallet_uuid}/operation")
def create_operation(wallet_uuid: str, request: WalletRequest,
                     db: Session = Depends(get_db)):
    """
    Эндпоинт для выполнения операции с кошельком. Обрабатывает операции пополнения
    и снятия средств на основе входных данных.

    Параметры:
    - wallet_uuid (str): UUID кошелька, с которым будет выполняться операция.
    - request (WalletRequest): Данные об операции (тип и сумма).

    Возвращает:
    - Статус выполнения операции (успех/неудача) и данные о транзакции.
    """
    try:

        # Обработка транзакции (пополнение или снятие средств)
        transaction = process_transaction(db, wallet_uuid, request.operationType,
                                          request.amount)

        # Возвращаем успешный ответ с информацией о транзакции
        return {"status": "success", "transaction": transaction}

    except (SQLAlchemyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))


# Эндпоинт для получения баланса кошелька
@app.get("/api/v1/wallets/{wallet_uuid}")
def get_wallet_balance(wallet_uuid: str, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения текущего баланса кошелька по его UUID.

    Параметры:
    - wallet_uuid (str): UUID кошелька, для которого нужно получить баланс.

    Возвращает:
    - Баланс кошелька или ошибку, если кошелек не найден.
    """
    try:
        # Получаем баланс кошелька с использованием функции get_balance
        balance = get_balance(db, wallet_uuid)

        # Если кошелек не найден, возвращаем ошибку с кодом 404
        if balance is None:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # Возвращаем текущий баланс кошелька
        return {"uuid": wallet_uuid, "balance": balance}

    except SQLAlchemyError as e:
        # В случае ошибки в базе данных возвращаем ошибку с кодом 500
        raise HTTPException(status_code=500, detail=f"Database error. {e}")
