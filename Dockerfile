# base image
FROM python:3.8.6

# update installer, install vi, less
RUN apt-get update && \
    apt-get install -y vim && \
    apt-get install -y less

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
COPY private/private_docker_config.yaml ./private/private_config.yaml

# install project
RUN python setup.py develop

# setup env variables
ENV PYSYS_CODE /usr/src/pysystemtrade
ENV SCRIPT_PATH $PYSYS_CODE/sysproduction/linux/scripts
ENV ECHO_PATH=/usr/src/echos

# set up PATH
RUN echo 'export PATH="$SCRIPT_PATH:$PATH"' >> ~/.bashrc
RUN echo 'export PYTHONPATH="$SCRIPT_PATH:$PYTHONPATH"' >> ~/.bashrc
