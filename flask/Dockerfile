FROM python:slim

RUN useradd py

WORKDIR /home/PyService

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
RUN mkdir db
#COPY migrations migrations
COPY run.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

RUN chown -R py:py ./
USER py

#EXPOSE 5000
ENTRYPOINT ["./boot.sh"]