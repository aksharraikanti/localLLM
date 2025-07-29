FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
ENTRYPOINT ["uvicorn", "scripts.run_inference_api:app", "--host", "0.0.0.0", "--port", "8000"]
