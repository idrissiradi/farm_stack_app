FROM python:3.10-alpine

# Create directory for the app user
RUN mkdir -p /home/ap

# Create the app user
RUN addgroup -S app && adduser -S -G app app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create the home directory
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install requirements
COPY requirements.txt /
RUN pip install -r /requirements.txt --no-cache-dir 

# Copy 
COPY . $APP_HOME

# Chown all the files to the app user
RUN chown -R app:app $APP_HOME

# Change to the app user
USER app