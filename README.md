# hse-tg-bot
Telegram bot for HSE students

How to run:
1) Install all requirements
2) Create 'credentials.json' file following instruction here:
https://developers.google.com/sheets/api/quickstart/python#authorize_credentials_for_a_desktop_application
3) Put 'credentials.json' to the working directory
4) Initialize database by executing 'migrate()' function in database.py
5) Place tg bots token in file 'config.py'
6) Run 'bot.py' file
7) Run 'request_functions.py' and log in your Google account
8) Done! Now you can use the bot


=======
# Бот-Ассистент v.2

Бот для помощи студентам ВШЭ


# Как запустить

1. Получаем токен для бота и кладём его в переменную среды `HSE_BOT_TOKEN`
2. Запускаем с помощью команды `docker-compose up --build`
3. Идём в бота [@UniOrgBot](https://t.me/UniOrgBot) и играемся
