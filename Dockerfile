FROM mcr.microsoft.com/playwright/python:v1.35.0-jammy
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
# ENTRYPOINT ["/tini", "-v", "--"]
WORKDIR /www
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY plugins/auditscript/requirements.txt plugins/auditscript/requirements.txt
RUN ls plugins/*/requirements.txt | xargs pip install -r 
COPY . /www
CMD [ "python3", "app.py" ]

