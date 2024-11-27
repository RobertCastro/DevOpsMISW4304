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

##Confguración New Relic
RUN pip install newrelic
ENV NEW_RELIC_APP_NAME="docker-flask-app-prod"
ENV NEW_RELIC_LOG=stdout
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
#INGEST_License
ENV NEW_RELIC_LICENSE_KEY=dcff61889f2dbca6013ef6954825e6fdFFFFNRAL
ENV NEW_RELIC_LOG_LEVEL=info
# etc.

ENTRYPOINT ["newrelic-admin", "run-program"]