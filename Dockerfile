FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV RDS_USERNAME=postgres
ENV RDS_PASSWORD=postgres
ENV RDS_HOSTNAME=host.docker.internal
ENV RDS_DB_NAME=postgres
ENV RDS_PORT=5432
ENV FLASK_PORT=5000

CMD python3 application.py --port $FLASK_PORT
