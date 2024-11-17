from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import process_transaction, get_balance
from app.database import get_db, lifespan_handler

from fastapi.responses import JSONResponse

# Инициализация FastAPI приложения с использованием lifespan
app = FastAPI(
    lifespan=lifespan_handler  # Используем обработчик lifespan
)


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


@app.post("/api/v1/wallets/{wallet_uuid}/operation")
async def create_operation(wallet_uuid: str, request: WalletRequest,
                           db: AsyncSession = Depends(get_db)):
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
        transaction = await process_transaction(db, wallet_uuid, request.operationType,
                                                request.amount)

        # Возвращаем успешный ответ с информацией о транзакции
        return {"status": "success", "transaction": transaction}

    except SQLAlchemyError as e:
        # Печатаем исключение и возвращаем ошибку 500
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        # Для других ошибок
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/v1/wallets/{wallet_uuid}")
async def get_wallet_balance(wallet_uuid: str, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для получения текущего баланса кошелька по его UUID.

    Параметры:
    - wallet_uuid (str): UUID кошелька, для которого нужно получить баланс.

    Возвращает:
    - Баланс кошелька или ошибку, если кошелек не найден.
    """
    try:
        # Получаем баланс кошелька
        balance = await get_balance(db, wallet_uuid)

        # Если кошелек не найден, возвращаем ошибку с кодом 404
        if balance is None:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # Возвращаем текущий баланс кошелька
        return {"uuid": wallet_uuid, "balance": balance}

    except SQLAlchemyError as e:
        # В случае ошибки в базе данных возвращаем ошибку с кодом 500
        raise HTTPException(status_code=500, detail=f"Database error. {e}")


# Обработка ошибок для неверного JSON
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid JSON provided. Please check the structure and data types.",
            "errors": exc.errors()  # Детали ошибки валидации
        }
    )
