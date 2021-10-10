from pprint import pprint
import time
import googleapiclient
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


def req_sheet_for_update(links, target_ranges, time_between_requests=30, requests_count=10,
                         troubleshoot_in_read_func=False, troubleshoot_mode=False):
    # Создаём list, содержащий начальные данные всех диапазонов по ссылкам
    data = [[] for _ in range(len(links))]
    if troubleshoot_mode:
        print('На вход было предоставлено следующее количество таблиц: ' + str(len(data)))
        print('Ссылки: ')
        for i in range(len(links)):
            print('link ' + str(i + 1) + ' ' + links[i])
    for i in range(len(data)):
        try:
            data[i] = read_range_from_sheet(links[i], target_ranges[i], troubleshoot_in_read_func)
            if troubleshoot_mode:
                print('Таблица №' + str(i + 1) + ' успешно подключена')
        except googleapiclient.errors.HttpError:
            print('Ошибка при работе с таблицей №' + str(i + 1) + ', проверьте верна ли сслыка')
    # Начинаем цикл обновления: каждые time_between_requests секунд проверяем данные каждой таблицы
    # Если они отличаются от хранимой нами версии - сообщаем об этом и перезаписываем данные
    print('Начинаю отслеживание изменений')
    if troubleshoot_mode:
        print('Время между обновлениями: ' + str(time_between_requests) + ' сек')
        print('Общее количество запросов: ' + str(requests_count))
    for req in range(requests_count):
        time.sleep(time_between_requests)
        if troubleshoot_mode:
            print('Происходит запрос №' + str(req + 1) + '...')
        for i in range(len(links)):
            try:
                new_data = read_range_from_sheet(links[i], target_ranges[i], troubleshoot_in_read_func)
                # TODO Сделать так, чтобы вместо номера показывалось название таблицы
                if new_data != data[i]:
                    print('В таблице №' + str(i + 1) + ' произошло изменение! \nСтарые данные:',
                          data[i], '\nНовые данные:', new_data)
                    data[i] = new_data
                elif troubleshoot_mode:
                    print('В таблице №' + str(i + 1) + ' изменений нет')
            except googleapiclient.errors.HttpError:
                if troubleshoot_mode:
                    print('Ошибка при работе с таблицей №' + str(i + 1) + ', проверьте верна ли сслыка')
                else:
                    pass
    print('Отслеживание изменений завершено')


def read_range_from_sheet(link=('https://docs.google.com/spreadsheets/d/1_q'
                                'MPqgcJZEJaiXZpMbjKM0trw_aGkkulrZG7Lq7kjU8/edit#gid=641725925'),
                          target_range='B10', troubleshoot_mode=False):
    # Парсим ссылку на таблицу
    list_of_link = link.split('/')
    if len(list_of_link) != 7:
        raise ValueError('Ссылка не соответсвует формату')
    spreadsheet_id = list_of_link[5]
    sheet_id = list_of_link[6].split('=')[1]
    if troubleshoot_mode:
        print('link = ' + link, 'spreadsheet_id = ' + spreadsheet_id, 'sheet_id = ' + sheet_id, sep='\n')

    # Здесь можно вручную поменять id документа и конкретной таблицы
    # spreadsheet_id = '1_qMPqgcJZEJaiXZpMbjKM0trw_aGkkulrZG7Lq7kjU8'
    # sheet_id = '641725925'
    # Здесь можно вручную задать range в котором будут выведены данные
    # target_range = 'A1:B2'

    # Название ключа
    credentials_file = 'creds.json'

    # Авторизация и получение объекта service (происходит магия, скопированная из открытых источников)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    http_auth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=http_auth)

    # Находим название листа таблицы
    sheet_title = None
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    if troubleshoot_mode:
        print('Список id листов в таблице:')
    for page in sheet_metadata['sheets']:
        if troubleshoot_mode:
            print(page['properties']['sheetId'])
        if page['properties']['sheetId'] == int(sheet_id):
            sheet_title = page['properties']['title']
    if sheet_title is None:
        raise ValueError('В таблице не найден лист с таким id')

    # Читаем и печатаем данные из заданного диапазона
    target_range = target_range.strip().upper()
    if troubleshoot_mode:
        print('range = ' + target_range)
    try:
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_title + '!' + target_range,
            majorDimension='ROWS'
        ).execute()
        return values['values']
    except googleapiclient.errors.HttpError:
        raise ValueError('Неверный формат диапазона range')

# Базовый тест:
# links_arr = ['https://docs.google.com/spreadsheets/d/1_qMcJZEJaiXZpMbjKM0trw_aGkkulrZG7Lq7kjU8/edit#gid=403770193',
#              'https://docs.google.com/spreadsheets/d/1csPjqocpnvlFp8IcoQdfGnbqT9jlS_jqjbgOFqB_sq8/edit#gid=0']
# ranges_arr = ['Y13', 'b3:e3']
# req_sheet_for_update(links_arr, ranges_arr, 15, 10, troubleshoot_mode=False)
