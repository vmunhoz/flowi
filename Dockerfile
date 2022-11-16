FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV PYTHON_VERSION=3.8
ENV POETRY_VERSION=1.1.6
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt update && \
    apt install --no-install-recommends -y build-essential software-properties-common && \
    apt install libgl1 ffmpeg libsm6 libxext6 -y

RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install --no-install-recommends -y python${PYTHON_VERSION} python${PYTHON_VERSION}-distutils python${PYTHON_VERSION}-venv python3-pip && \
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
# RUN pip install "poetry==$POETRY_VERSION" && \
#     poetry --version
RUN apt-get update -y && \
    apt-get install curl -y && \
    bash -c 'curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0'


COPY pyproject.toml poetry.lock ./
RUN /root/.local/bin/poetry --version && \
    /root/.local/bin/poetry export --without-hashes -f requirements.txt -o requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY flowi/ ./flowi/

RUN mkdir -p /airflow/xcom/
