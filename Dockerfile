ARG PYTHON_VERSION=3.11-slim-buster

FROM python:${PYTHON_VERSION}
RUN useradd -ms /bin/bash dzskills

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN mkdir -p /home/dzskills/code
RUN chown -R dzskills:dzskills /home/dzskills/code/
USER dzskills

WORKDIR /home/dzskills/code

COPY requirements.txt /tmp/requirements.txt
ENV PATH="${PATH}:/home/dzskills/.local/bin"
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

COPY . .

#ENV SECRET_KEY "o2ElMgbjdfMOHsQ6dJqXWxVnkbadir2WeyzeTFl5MjCHYQlbpR"
#ENV DATABASE_URL="postgres://dzskills:mFkAxxgeYQryzU2@dzskills-db.flycast:5432/dzskills?sslmode=disable"
USER root
RUN chown -R dzskills:dzskills /home/dzskills/code/
USER dzskills
RUN python manage.py collectstatic --noinput
RUN python3 manage.py migrate --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "4", "backend.wsgi"]
