FROM python:3.8.6

RUN mkdir /usr/src/echos
WORKDIR /usr/src/pysystemtrade
COPY requirements.txt ./
#RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install nose
#RUN pip install flake8

COPY . .

RUN python setup.py develop

ENV PYSYS_CODE /usr/src/pysystemtrade
ENV SCRIPT_PATH $PYSYS_CODE/sysproduction/linux/scripts
ENV ECHO_PATH=/usr/src/echos

#RUN chmod +x $PYSYS_CODE/sysproduction/linux/scripts/interactive_diagnostics

#CMD [ "python", "./your-daemon-or-script.py" ]
#CMD [ "python", "sysinit/futures/repocsv_spotfx_prices.py" ]
#CMD [ "python", "examples/introduction/asimpletradingrule.py" ]
#CMD [ "python" ]
CMD [ "bash" ]
#CMD ["tail", "-f", "/dev/null"]



#COPY pysystemtrade/ /pysystemtrade/
#ENV PYTHONPATH /pysystemtrade:$PYTHONPATH
#CMD [ "python3", "/pysystemtrade/examples/dockertest/dockertest.py" ]