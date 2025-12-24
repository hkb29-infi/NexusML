FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /workspace

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    redis \
    pyyaml \
    tensorboard \
    wandb

# Copy training templates
COPY worker/templates /workspace/templates
COPY worker/executor /workspace/executor

CMD ["python", "-m", "executor.main"]

