import os
import requests
import telegram
import time
from dotenv import load_dotenv
import logging

logging.basicConfig(filename='app.log', filemode='w',
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
BOT = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        send_message('ValueError: Homework name is None. Bot shuts down')
        logging.error('ValueError: Homework name is None. Bot shuts down')
        raise ValueError('Homework name is None')

    if homework.get('status') is None:
        logging.error('Homework status in None')
        raise ValueError('Homework status in None')

    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему ' \
                  'уроку.'
    else:
        send_message('Unknown homework status. Bot shuts down')
        logging.error('Unknown homework status')
        raise ValueError('Unknown homework status')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, params=params, headers=headers)
        return homework_statuses.json()
    except requests.exceptions as e:
        send_message(f'Error with requests: {e}')
        logging.exception('Error!')
        raise e


def send_message(message):
    return BOT.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                'current_date')
            time.sleep(300)

        except Exception as e:
            send_message(f'Error: {e}')
            logging.exception(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
