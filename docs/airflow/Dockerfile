FROM python:3.6

# Set Env's
ENV AIRFLOW_HOME=/usr/local/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow USER_ID=8888

USER root
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} --uid ${USER_ID} airflow

# Set version
ARG AIRFLOW_VERSION=2.0.2

# Install
RUN apt-get update -y && \
    apt-get install -y apt-utils libsasl2-dev

RUN pip install apache-airflow['kubernetes'] apache-airflow-providers-cncf-kubernetes
RUN apt-get update -y && \
    apt-get install expect -y

# Start
COPY ./scripts/* ${AIRFLOW_HOME}/

RUN mkdir ${AIRFLOW_HOME}/dags/
COPY dags/* ${AIRFLOW_HOME}/dags/

RUN chown -R airflow: ${AIRFLOW_HOME}

RUN chmod 777 ${AIRFLOW_HOME} -R


WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 8080
