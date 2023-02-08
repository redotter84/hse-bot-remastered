FROM python:3.9
WORKDIR ./bot
COPY requirements.txt .
RUN pip install -r ./requirements.txt
COPY . .
RUN python3 ./database.py
ENTRYPOINT ./run.sh
