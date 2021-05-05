from python:3.8

# ENV POETRY_VERSION=1.1.6
#
# RUN pip install "poetry==$POETRY_VERSION" && \
#     poetry --version
#
# COPY poetry.lock pyproject.toml ./
# RUN poetry install --no-dev && \
#     rm -rf ~/.cache/pypoetry/{cache,artifacts}

RUN pip install flowi --no-cache-dir
