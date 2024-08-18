FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5555 5556

CMD ["python", "servidor.py"]
