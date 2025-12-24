FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend /app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
