import time
import googleapiclient
import httplib2
import apiclient
import asyncio
from oauth2client.service_account import ServiceAccountCredentials
from database import get_all_sheet_subscriptions
from send_message_function import send_message


async def req_sheets_for_update(time_between_requests=30, requests_count=10, troubleshoot_in_read_func=False,
                          troubleshoot_mode=False):
    # Создаём list, содержащий начальные данные всех диапазонов по ссылкам
    subscriptions_list = get_all_sheet_subscriptions()
    data = dict()
    if troubleshoot_mode:
        print('На вход было предоставлено следующее количество таблиц: ' + str(len(subscriptions_list)))
        print('Ссылки: ')
        for i in range(len(subscriptions_list)):
            print('link id: ' + str(subscriptions_list[i].id) + ' ' + subscriptions_list[i].sheet_link)
    for i in range(len(subscriptions_list)):
        try:
            data[subscriptions_list[i].id], _ = await read_range_and_title_from_sheet(subscriptions_list[i].sheet_link,
                                                                                      subscriptions_list[i].sheet_range,
                                                                                      troubleshoot_in_read_func)
            if troubleshoot_mode:
                print('Таблица №' + str(subscriptions_list[i].id) + ' успешно подключена')
        except googleapiclient.errors.HttpError:
            print('Ошибка при работе с подпиской ' + str(subscriptions_list[i].id) + ', проверьте верна ли сслыка')
        except httplib2.error.ServerNotFoundError:
            print('Что-то пошло не так')

    # Начинаем цикл обновления: каждые time_between_requests секунд проверяем данные каждой таблицы
    # Если они отличаются от хранимой нами версии - сообщаем об этом и перезаписываем данные
    if troubleshoot_mode:
        print('Время между обновлениями: ' + str(time_between_requests) + ' сек')
        print('Общее количество запросов: ' + str(requests_count))
    for req in range(requests_count):
        time.sleep(time_between_requests)
        if troubleshoot_mode:
            print('Происходит запрос №' + str(req + 1) + '...')

        new_new_data = dict()
        subscriptions_list = get_all_sheet_subscriptions()
        for el in subscriptions_list:
            if el.id in data:
                new_new_data[el.id] = data[el.id]
            else:
                try:
                    new_new_data[el.id], sheet_title = await read_range_and_title_from_sheet(el.sheet_link,
                                                                                             el.sheet_range)
                except googleapiclient.errors.HttpError:
                    print(
                        'Ошибка при работе с подпиской ' + str(el.id) + ', проверьте верна ли сслыка')
                except httplib2.error.ServerNotFoundError:
                    print('Что-то пошло не так')
        data = new_new_data.copy()

        for el in subscriptions_list:
            try:
                new_data, sheet_title = await read_range_and_title_from_sheet(el.sheet_link, el.sheet_range,
                                                                              troubleshoot_in_read_func)
                if new_data != data[el.id]:
                    await send_message(el.user_id, f'В таблице "{str(sheet_title)}" по подписке № {str(el.id)} '
                                       f'произошло изменение!\nСтарые данные: '
                                       f'{data[el.id]}, \nНовые данные: {new_data}')
                    data[el.id] = new_data
                elif troubleshoot_mode:
                    print('В таблице №' + str(el.id) + ' изменений нет')
            except googleapiclient.errors.HttpError:
                if troubleshoot_mode:
                    print('Ошибка при работе с таблицей №' + str(el.id) + ', проверьте верна ли сслыка')
                else:
                    pass


async def read_range_and_title_from_sheet(link, target_range, troubleshoot_mode=False):
    # Парсим ссылку на таблицу
    list_of_link = link.split('/')
    if len(list_of_link) != 7:
        raise ValueError('Ссылка не соответсвует формату')
    spreadsheet_id = list_of_link[5]
    if list_of_link[6] == 'edit':
        list_of_link[6] = 'edit#gid=0'
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
    service = apiclient.discovery.build('sheets', 'v4', http=http_auth, cache_discovery=False)

    # Находим название листа таблицы
    sheet_page = None
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    if troubleshoot_mode:
        print('Список id листов в таблице:')
    for page in sheet_metadata['sheets']:
        if troubleshoot_mode:
            print(page['properties']['sheetId'])
        if page['properties']['sheetId'] == int(sheet_id):
            page_title = page['properties']['title']
    if page_title is None:
        raise ValueError('В таблице не найден лист с таким id')

    # Находим название самой таблицы
    sheet_title = sheet_metadata['properties']['title']

    # Читаем и печатаем данные из заданного диапазона
    target_range = target_range.strip().upper()
    if troubleshoot_mode:
        print('range = ' + target_range)
    try:
        req_answer = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=page_title + '!' + target_range,
            majorDimension='ROWS'
        ).execute()
        if 'values' not in req_answer.keys():
            req_answer['values'] = [['']]
        return req_answer['values'], sheet_title
    except googleapiclient.errors.HttpError:
        raise ValueError('Неверный формат диапазона range')


if __name__ == "__main__":
    asyncio.run(req_sheets_for_update(requests_count=1000, troubleshoot_in_read_func=True, troubleshoot_mode=True))

# Базовый тест:
# links_arr = ['https://docs.google.com/spreadsheets/d/1_qMPqgcJZEJaiXZpMbjKM0trw_aGkkulrZG7Lq7kjU8/edit#gid=403770193',
#              'https://docs.google.com/spreadsheets/d/1csPjqocpnvlFp8IcoQdfGnbqT9jlS_jqjbgOFqB_sq8/edit#gid=0']
# ranges_arr = ['Y13', 'b3:e3']
# req_sheets_for_update(links_arr, ranges_arr, 15, 10, troubleshoot_in_read_func=False, troubleshoot_mode=True)

#req_sheets_for_update(20, 10, troubleshoot_in_read_func=False, troubleshoot_mode=True)
