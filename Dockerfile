FROM nvidia/cuda:10.1-cudnn7-runtime

ENV PYTHON_VERSION=3.8
ENV POETRY_VERSION=1.1.6

RUN apt update && \
    apt install --no-install-recommends -y build-essential software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y python${PYTHON_VERSION} python3-pip python3-setuptools python3-distutils && \
    cd /usr/bin && \
    ln -sf python${PYTHON_VERSION}         python3 && \
    ln -sf python${PYTHON_VERSION}m        python3m && \
    ln -sf python${PYTHON_VERSION}-config  python3-config && \
    ln -sf python${PYTHON_VERSION}m-config python3m-config && \
    ln -sf python3                         /usr/bin/python && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir --upgrade setuptools wheel six

WORKDIR flowi
RUN pip install "poetry==$POETRY_VERSION" && \
    poetry --version

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install && \
    rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY flowi/ ./flowi/

RUN mkdir -p /airflow/xcom/

RUN apt-get update && apt-get install libgl1 -y
RUN apt-get install ffmpeg libsm6 libxext6 -y
