FROM python:3.10
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "-v", "--"]
WORKDIR /www
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /www
CMD [ "python3", "app.py" ]

