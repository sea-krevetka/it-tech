FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Не устанавливаем DEBUG тут - через переменные окружения
ENV DEBUG=False
ENV PORT=8283

# Создаем непривилегированного пользователя
RUN adduser --system --uid 1001 appuser
USER appuser

EXPOSE 8283

# Команда запуска (без hardcoded секретов)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8283"]