# base image
FROM python:3.8.6

# update installer, install vi, less, cron
RUN apt-get update && \
    apt-get install -y vim && \
    apt-get install -y less && \
    apt-get install -y cron

# update pip
RUN python -m pip install --upgrade pip

# define echos dir
RUN mkdir /usr/src/echos

# set working dir
WORKDIR /usr/src/pysystemtrade

# copy dependencies definition
COPY requirements.txt ./

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy whole project to image (except entries in .dockerignore)
COPY . .

# copy docker specific config
COPY private/private_docker_config_syno.yaml ./private/private_config.yaml

# setup cron
COPY examples/docker/crontab /etc/cron.d/sysjobs
RUN chmod 0644 /etc/cron.d/sysjobs
ENV PYTHONUNBUFFERED 1

# install project
RUN python setup.py develop

# setup env variables
ENV PYSYS_CODE /usr/src/pysystemtrade
ENV SCRIPT_PATH $PYSYS_CODE/sysproduction/linux/scripts
ENV ECHO_PATH=/usr/src/echos

# set up PATH
RUN echo 'export PATH="$SCRIPT_PATH:$PATH"' >> ~/.bashrc
RUN echo 'export PYTHONPATH="$SCRIPT_PATH:$PYTHONPATH"' >> ~/.bashrc

# keep the container running
CMD cron -f
#CMD tail -F /dev/null