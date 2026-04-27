FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim

LABEL maintainer="student-s01"
LABEL description="Invoices Service for week-10"
LABEL project_code="invoices-s01"

WORKDIR /app

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .

RUN find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

USER appuser

EXPOSE 8268

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8268/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8268"]