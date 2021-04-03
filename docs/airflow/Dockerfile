FROM python:3.6


# Set Env's
ENV AIRFLOW_HOME=/usr/local/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow USER_ID=8888

USER root
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} --uid ${USER_ID} airflow

# Set version
ARG AIRFLOW_VERSION=2.0.1

# Install
RUN apt-get update -y && \
    apt-get install -y apt-utils libsasl2-dev
RUN pip install --upgrade pip \
    && pip install psycopg2-binary \
    && pip install -U pip setuptools wheel \
    && pip install pytz \
    && pip install pyOpenSSL \
    && pip install ndg-httpsclient \
    && pip install pyasn1 \
    && pip install --no-cache-dir apache-airflow['crypto','celery','kubernetes','postgres','hive']==${AIRFLOW_VERSION} \
    && pip install cryptography \
    && pip install 'redis==3.2' SQLAlchemy \
    && if [ -n "${PYTHON_DEPS}" ]; then pip install ${PYTHON_DEPS}; fi \
    && pip install apache-airflow-providers-cncf-kubernetes \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base
RUN apt-get update -y && \
    apt-get install expect -y

# Start
COPY ./scripts/* ${AIRFLOW_HOME}/
COPY airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

RUN mkdir ${AIRFLOW_HOME}/dags/
COPY dags/* ${AIRFLOW_HOME}/dags/
COPY kubeconfig.yaml ${AIRFLOW_HOME}/kubeconfig.yaml

RUN chown -R airflow: ${AIRFLOW_HOME}

RUN chmod 777 ${AIRFLOW_HOME} -R

ENV KUBECONFIG=/usr/local/airflow/kubeconfig.yaml

WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 8080
