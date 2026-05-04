FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY main.py app.py openapi.yaml ./
COPY agent ./agent
COPY tools ./tools
COPY setup/__init__.py setup/db_config.py ./setup/

EXPOSE 8092

CMD ["python", "main.py"]
