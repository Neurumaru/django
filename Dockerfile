# ./Dockerfile
FROM python:3

WORKDIR /usr/src/app

# Install packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY django_project ./django_project
