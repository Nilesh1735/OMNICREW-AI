FROM python:3.11-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Install Playwright browsers AND required OS dependencies
RUN playwright install --with-deps chromium

COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]