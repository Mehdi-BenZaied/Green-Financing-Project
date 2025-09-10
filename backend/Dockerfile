FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "python wait_for_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
