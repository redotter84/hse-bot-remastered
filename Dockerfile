FROM python:3.9
COPY requirements.txt ./bot/
RUN pip install -r ./bot/requirements.txt
COPY . ./bot
RUN python3 ./bot/database.py
ENTRYPOINT python3 ./bot/bot.py
