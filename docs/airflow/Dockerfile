FROM centos/python-38-centos7

# Set Env's
ENV AIRFLOW_HOME=/usr/local/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow USER_ID=8888

USER root
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} --uid ${USER_ID} airflow

# Set version
ARG AIRFLOW_VERSION=2.0.2

# Install
RUN yum update -y && \
    yum install wget tar gzip gcc make expect docker nano -y

RUN wget https://www.sqlite.org/src/tarball/sqlite.tar.gz && \
    tar xzf sqlite.tar.gz && \
    cd sqlite/  && \
    export CFLAGS="-DSQLITE_ENABLE_FTS3 \
        -DSQLITE_ENABLE_FTS3_PARENTHESIS \
        -DSQLITE_ENABLE_FTS4 \
        -DSQLITE_ENABLE_FTS5 \
        -DSQLITE_ENABLE_JSON1 \
        -DSQLITE_ENABLE_LOAD_EXTENSION \
        -DSQLITE_ENABLE_RTREE \
        -DSQLITE_ENABLE_STAT4 \
        -DSQLITE_ENABLE_UPDATE_DELETE_LIMIT \
        -DSQLITE_SOUNDEX \
        -DSQLITE_TEMP_STORE=3 \
        -DSQLITE_USE_URI \
        -O2 \
        -fPIC" && \
    export PREFIX="/usr/local"  && \
    LIBS="-lm" ./configure --disable-tcl --enable-shared --enable-tempstore=always --prefix="$PREFIX"  && \
    make  && \
    make install

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN pip install --no-cache-dir \
    apache-airflow['kubernetes']==2.1.0 apache-airflow-providers-cncf-kubernetes==1.2.0 pymongo==3.11.4 kubernetes awscli
RUN yum update -y && \
    yum install expect -y

# Start
COPY ./scripts/* ${AIRFLOW_HOME}/

RUN mkdir ${AIRFLOW_HOME}/dags/
COPY dags/ ${AIRFLOW_HOME}/dags/
COPY airflow.cfg ${AIRFLOW_HOME}/

RUN chown -R airflow: ${AIRFLOW_HOME}

RUN chmod 777 ${AIRFLOW_HOME} -R
RUN chmod +x ${AIRFLOW_HOME}/dags/deploy/docker_build_api.sh
RUN chmod +x ${AIRFLOW_HOME}/dags/deploy/docker_build_batch.sh

WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 8080
