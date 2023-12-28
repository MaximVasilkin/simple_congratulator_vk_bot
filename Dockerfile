FROM python:3.10-alpine

WORKDIR /vk_bot
COPY ./app ./
RUN pip install -r requirements.txt

CMD python3 main.py
