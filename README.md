2) Create 'credentials.json' file following instruction here:
https://developers.google.com/sheets/api/quickstart/python#authorize_credentials_for_a_desktop_application
3) Put 'credentials.json' to the working directory

6) Run 'bot.py' file
7) Run 'request_functions.py' and log in your Google account
8) Done! Now you can use the bot


=======
# Бот-Ассистент v.2

Бот для помощи студентам ВШЭ


# Как запустить

1. Создаём приложение (не забываем подключить его к Google Sheets API) и service account согласно [инструкции](https://support.google.com/a/answer/7378726). Путь до скачанного JSON-файла кладём в переменную среды `HSE_BOT_GOOGLE_SERVICE_ACCOUNT`
2. Получаем токен для бота и кладём его в переменную среды `HSE_BOT_TG_TOKEN`
3. Запускаем с помощью команды `docker-compose up --build`
4. Проходим по указанной
3. Идём в бота [@UniOrgBot](https://t.me/UniOrgBot) и играемся
