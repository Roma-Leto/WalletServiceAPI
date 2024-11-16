from sqlalchemy.orm import Session
from app.models import Wallet
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


# Функция для обработки операции с кошельком (пополнение или снятие)
def process_transaction(db: Session, wallet_uuid: str, operation_type: str,
                        amount: int):
    """
    Обрабатывает операцию пополнения или снятия средств с кошелька.

    Параметры:
    - db (Session): Сессия SQLAlchemy для работы с базой данных.
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
    # Получаем кошелек по его UUID
    wallet = db.query(Wallet).filter(wallet_uuid == Wallet.uuid).first()

    # Если кошелек не найден, выбрасываем исключение с кодом 404
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
        db.commit()  # Подтверждаем изменения
        db.refresh(wallet)  # Обновляем объект кошелька, чтобы получить актуальные данные
        return {"uuid": wallet.uuid, "balance": wallet.balance}  # Возвращаем сериализуемый словарь
    except IntegrityError:
        # В случае ошибки базы данных откатываем изменения
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


# Функция для получения баланса кошелька
def get_balance(db: Session, wallet_uuid: str):
    """
    Получает текущий баланс кошелька по его UUID.

    Параметры:
    - db (Session): Сессия SQLAlchemy для работы с базой данных.
    - wallet_uuid (str): UUID кошелька, для которого нужно получить баланс.

    Возвращает:
    - Баланс кошелька в виде целого числа, если кошелек существует.
    - None, если кошелек не найден.
    """
    # Получаем кошелек по его UUID
    wallet = db.query(Wallet).filter(Wallet.uuid == wallet_uuid).first()

    # Если кошелек не найден, возвращаем None
    if not wallet:
        return None

    # Возвращаем текущий баланс кошелька
    return wallet.balance
