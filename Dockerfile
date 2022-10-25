# ./Dockerfile
FROM python
WORKDIR /usr/src/app

# Install packages
COPY . .
RUN pip install -r requirements.txt

# Ports
EXPOSE 80
EXPOSE 443
