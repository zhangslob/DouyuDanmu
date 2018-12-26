FROM python:3.6

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
CMD ["python", "douyu_websocket_client.py"]