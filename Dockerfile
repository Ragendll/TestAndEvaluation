FROM python:3.13-slim

WORKDIR /app

# Чтобы быстрее пересобирать: сначала зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом код
COPY . .

EXPOSE 8000

CMD ["uvicorn", "digital_company_ai_support.main:app", "--host", "0.0.0.0", "--port", "8000"]