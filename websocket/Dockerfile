FROM python:3.7.11-slim

ARG DOCKER_HOME="/opt/yijun"
ARG DOCKER_CODE="/opt/yijun/code"
ARG DOCKER_USER="yijun"
ARG DOCKER_UID=5000

RUN apt-get update && apt-get install -y gcc libpq-dev

RUN useradd -d ${DOCKER_HOME} -m -U -u ${DOCKER_UID} ${DOCKER_USER}

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

RUN apt-get purge -y gcc

USER ${DOCKER_USER}

WORKDIR ${DOCKER_CODE}

ENV PYTHONPATH=.

COPY --chown=${DOCKER_USER} . .

EXPOSE 5000
 
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "4", "-k", "gevent", "main:app"]
