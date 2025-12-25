FROM python:3.9-slim
WORKDIR /
COPY backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r /backend/requirements.txt
COPY backend /backend
ENV PYTHONPATH=/
CMD ["python", "-m", "backend.api.main"]
