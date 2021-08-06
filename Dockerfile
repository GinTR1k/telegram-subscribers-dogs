FROM python:3.9-slim

RUN useradd -m -s /bin/bash app
WORKDIR /home/app
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh && ln -s /usr/local/bin/entrypoint.sh /

ADD . .

RUN chown -R app:app /home/app
USER app

ENTRYPOINT ["/entrypoint.sh"]
