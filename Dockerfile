# ./Dockerfile
FROM python:3
WORKDIR /usr/src/app

# Install packages
COPY . .
RUN pip3 install -r requirements.txt

# Ports
EXPOSE 80
EXPOSE 443
