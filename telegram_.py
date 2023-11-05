import requests
import json
from setLogger import get_logger

logger = get_logger(__name__)


# with open('config.json') as f:
#     config = json.load(f)

# token = config['telegramToken']
# id = config['telegramId']


def send_to_telegram(text):
	text = str(text)
	send_text = f'https://api.telegram.org/bot{token}/SendMessage?chat_id={id_}&parse_mode=Markdown&text={text}'
	response = requests.get(send_text)
	return response.json()



def sendPhoto(img, token, id_):
    img = open(img, 'rb')
    url = f"https://api.telegram.org/bot{token}/SendPhoto?chat_id={id_}"
    response = requests.get(url, files={'photo': img})
    return response.json()

# print(sendPhoto("BTC-USDT-3m"))
