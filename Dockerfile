FROM python:3.11-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Выводим значение переменной окружения DATABASE_URL
RUN echo "DATABASE_URL is: $DATABASE_URL"

# Копируем код приложения
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем приложение с помощью Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Запускаем приложение с задержкой
#CMD /bin/sh -c "sleep 10 && uvicorn app.main:app --host 0.0.0.0 --port 8000"
