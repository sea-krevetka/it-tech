# Stage 1: Builder
# FROM python:3.11 as builder
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --user -r requirements.txt

# Stage 2: Runtime
# FROM python:3.11-slim
# WORKDIR /app
# COPY --from=builder /root/.local /root/.local
# COPY . .
# ENV PATH=/root/.local/bin:$PATH

# EXPOSE 8000
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
