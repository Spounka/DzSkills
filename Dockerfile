ARG PYTHON_VERSION=3.11-slim-buster

FROM python:${PYTHON_VERSION}
RUN useradd -m dzskills
USER dzskills

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN mkdir -p /home/dzskills/code

WORKDIR /home/dzskills/code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf ~/.cache/
COPY . .
USER root
RUN chown dzskills:dzskills /home/dzskills/code -R
USER dzskills

#ENV SECRET_KEY "o2ElMgbjdfMOHsQ6dJqXWxVnkbadir2WeyzeTFl5MjCHYQlbpR"
#ENV DATABASE_URL="postgres://dzskills:mFkAxxgeYQryzU2@dzskills-db.flycast:5432/dzskills?sslmode=disable"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

#CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "backend.wsgi"]
