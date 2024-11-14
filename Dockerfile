FROM public.ecr.aws/docker/library/python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV RDS_USERNAME=postgres
ENV RDS_PASSWORD=secret-database-password
ENV RDS_HOSTNAME=postgres-instance.cl0qmecqm1hz.us-west-2.rds.amazonaws.com
ENV RDS_DB_NAME=postgres
ENV RDS_PORT=5432
ENV FLASK_PORT=5000

CMD python3 application.py --port $FLASK_PORT
