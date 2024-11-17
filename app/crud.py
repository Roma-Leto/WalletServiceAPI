from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Wallet
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


async def process_transaction(db: AsyncSession, wallet_uuid: str, operation_type: str, amount: int):
    """
    Обрабатывает операцию пополнения или снятия средств с кошелька.

    Параметры:
    - db (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
    - wallet_uuid (str): UUID кошелька, с которым выполняется операция.
    - operation_type (str): Тип операции, может быть "DEPOSIT" (пополнение) или "WITHDRAW"
    (снятие).
    - amount (int): Сумма для операции.

    Возвращает:
    - Обновленный объект кошелька с новым балансом после успешной операции.

    Исключения:
    - HTTPException(404): Если кошелек с данным UUID не найден.
    - HTTPException(400): Если операция "WITHDRAW" не может быть выполнена из-за
    недостатка средств, или если указан неверный тип операции.
    - HTTPException(500): Если произошла ошибка базы данных.
    """
    # Получаем кошелек по UUID
    async with db.begin():  # Используем асинхронную транзакцию
        result = await db.execute(select(Wallet).filter(Wallet.uuid == wallet_uuid))
        wallet = result.scalar_one_or_none()  # Получаем единственный результат

        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # Выполняем операцию в зависимости от типа операции
        if operation_type == "DEPOSIT":
            wallet.balance += amount  # Пополнение баланса
        elif operation_type == "WITHDRAW":
            # Проверяем, хватает ли средств на балансе для снятия
            if wallet.balance < amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            wallet.balance -= amount  # Снятие средств
        else:
            # Если тип операции не соответствует ни "DEPOSIT", ни "WITHDRAW"
            raise HTTPException(status_code=400, detail="Invalid operation type")

        # Попытка сохранить изменения в базе данных
        try:
            await db.commit()  # Подтверждаем изменения
            return {"uuid": wallet.uuid, "balance": wallet.balance}  # Возвращаем сериализуемый словарь
        except IntegrityError:
            # В случае ошибки базы данных откатываем изменения
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error")


async def get_balance(db: AsyncSession, wallet_uuid: str):
    """
    Получает текущий баланс кошелька по его UUID.

    Параметры:
    - db (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
    - wallet_uuid (str): UUID кошелька, для которого нужно получить баланс.

    Возвращает:
    - Баланс кошелька в виде целого числа, если кошелек существует.
    - None, если кошелек не найден.
    """
    # Получаем кошелек по его UUID
    result = await db.execute(select(Wallet).filter(Wallet.uuid == wallet_uuid))
    wallet = result.scalar_one_or_none()  # Получаем результат запроса

    if not wallet:
        return None

    # Возвращаем текущий баланс кошелька
    return wallet.balance
