# Бот-Ассистент v.2

Бот для помощи студентам ВШЭ


# Как запустить

1. Создаём приложение (не забываем подключить его к Google Sheets API) и service account согласно [инструкции](https://support.google.com/a/answer/7378726). Путь до скачанного JSON-файла кладём в переменную среды `HSE_BOT_GOOGLE_SERVICE_ACCOUNT`
2. Получаем токен для бота и кладём его в переменную среды `HSE_BOT_TG_TOKEN`
3. Запускаем с помощью команды `docker-compose up --build`
4. Идём в бота [@UniOrgBot](https://t.me/UniOrgBot) и играемся
