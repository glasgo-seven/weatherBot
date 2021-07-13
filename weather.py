WEATHER = {
	'Sunny'						:	['Солнечно', '\U00002600'],
	'Mostly Sunny'				:	['Преимущественно солнечно', '\U0001F324'],

	'Partly Cloudy'				:	['Переменная облачность', '\U0001F325'],
	'Mostly Cloudy'				:	['Облачно с прояснениями', '\U0001F325'],
	'Cloudy'					:	['Облачно', '\U00002601'],

	'Isolated Showers'			:	['Местами дождь', '\U0001F326'],
	'Scattered Showers'			:	['Рассеянный дождь', '\U0001F326'],
	'Rain'						:	['Дождь', '\U0001F327'],
	'Isolated Thunderstorms'	:	['Местами грозы', '\U000026C8'],
	'Scattered Thunderstorms'	:	['Рассеянные грозы', '\U000026C8'],
	'Thunderstorm'				:	['Гроза', '\U0001F329'],

	'Wind'						:	['Ветренно', '\U0001F32C'],
	'Foggy'						:	['Туман', '\U0001F32B'],

	'Clear Night'				:	['Ясно, ночь', '\U00002728'],
	'Partly Cloudy Night'		:	['Переменная облачность, ночь', '\U0001F319'],
	'Partly Clear Night'		:	['Облачно с прояснениями, ночь', '\U0001F319'],
	'Mostly Cloudy Night'		:	['Облачно с прояснениями, ночь', '\U0001F315'],
	'Mostly Clear Night'		:	['Переменная облачность, ночь', '\U0001F315'],
}

from bs4 import BeautifulSoup
import requests as req
import sys

from alert import *

def get_weather(message, location):
	try:
		resp = req.get(f"https://weather.com/ru-RU/weather/today/l/{location}")

		soup = BeautifulSoup(resp.text, 'lxml')

		loc = soup.find('div', id='WxuHeaderLargeScreen-header-9944ec87-e4d4-4f18-b23e-ce4a3fd8a3ba').find_all('span')
		lang = loc[0].text
		deg = loc[1].text[-1]

		grind = soup.find('div', id='WxuCurrentConditions-main-b3094163-ef75-4558-8d9a-e35e6b9b1034')
		now_loca = grind.h1.text
		now_temp = grind.span.text
		now_weat = grind.title.text

		try:
			if lang == 'RU':
				now_weat_t = WEATHER[now_weat][0]
			else:
				now_weat_t = now_weat
			now_weat_i = WEATHER[now_weat][1]
		except:
			now_weat_t = now_weat
			now_weat_i = ''
		week = soup.find('div', id='WxuDailyWeatherCard-main-bb1a17e7-dc20-421a-b1b8-c117308c6626').find_all('li')

		if lang == 'RU':
			res = f'{now_loca}\nСейчас:⠀{now_temp}{deg}\n{now_weat_i}⠀{now_weat_t}\n'
		else:
			res = f'{now_loca}\nNow:⠀{now_temp}{deg}\n{now_weat_i}⠀{now_weat_t}\n'

		for we in week:
			divs = we.find_all('div')
			try:
				if lang == 'RU':
					weather_t = WEATHER[we.title.text][0]
				else:
					weather_t = we.title.text
				weather_i = WEATHER[we.title.text][1]
			except:
				weather_t = we.title.text
				weather_i = ''
			if lang == 'RU':
				res += f'\n{we.h3.text.upper()}⠀-⠀{weather_i}⠀{weather_t}\n⠀⠀День:⠀{divs[0].text}{deg}\n⠀⠀Ночь:⠀{divs[1].text}{deg}'
			else:
				res += f'\n{we.h3.text.upper()}⠀-⠀{weather_i}⠀{weather_t}\n⠀⠀Day:⠀{divs[0].text}{deg}\n⠀⠀Night:⠀{divs[1].text}{deg}'

		return res
	except:
		error(f"[ ERROR ] in GET_WEATHER of USER-{message.from_user.id} : {sys.exc_info()[0]}.")
		return None

# print(get_weather('55.75,37.58'))
