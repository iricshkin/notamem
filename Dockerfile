FROM python:3.13.3-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src/configs/settings-example.yaml ./configs/
RUN pip install --no-cache-dir uv
RUN uv pip install --system -r pyproject.toml
COPY src/ ./src/
COPY src/configs/alembic.ini ./configs/
CMD ['uvicorn', 'src.main:app']
