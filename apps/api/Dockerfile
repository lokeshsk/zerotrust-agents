FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (including Postgres drivers)
RUN apt-get update && apt-get install -y curl libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY requirements.txt .
# Install dependencies into system environment for Docker
RUN pip install --no-cache-dir -r requirements.txt
# Force install extra dependencies to ensure they are available.
RUN pip install --no-cache-dir httpx passlib[bcrypt] python-multipart

COPY . .

# Ensure data directory exists for SQLite
RUN mkdir -p /app/data

EXPOSE 8001
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8001"]
