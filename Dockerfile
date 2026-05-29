FROM python:3.10-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "bot.py"]