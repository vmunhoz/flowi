FROM python:3.8

#ENV POETRY_VERSION=1.1.6

WORKDIR flowi
#RUN pip install "poetry==$POETRY_VERSION" && \
#    poetry --version
#
#COPY pyproject.toml poetry.lock ./
#RUN poetry install  && \
#    rm -rf ~/.cache/pypoetry/{cache,artifacts}

#COPY flowi/ ./
RUN pip install --no-cache-dir flowi
