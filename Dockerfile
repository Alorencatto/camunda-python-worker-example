
# set base image python:3.8-slim-buster
FROM python:3.8-slim-buster

# set working directory as app
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

# command to run when image is executed inside a container
CMD [ "python3", "app.py" ]
#CMD [ "python3", "test-worflow.py" ]
