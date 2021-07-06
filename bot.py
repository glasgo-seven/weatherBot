#!/usr/bin/env python
# coding: utf-8

import codecs
import os
from random import randint
from time import time, sleep
import sys

import telebot
from telebot import types

from alert import *
from weather import get_weather

def get_credentails():
	try:
		f = open('./firebase.json', 'r')
		f.close()
		return './firebase.json'
	except FileNotFoundError:
		return os.getenv('BOT_FIREBASE_CREDENTAILS')

import firebase_admin
from firebase_admin import db, firestore
from google.cloud.firestore_v1 import ArrayUnion, Increment

cred_obj = firebase_admin.credentials.Certificate(get_credentails())
default_app = firebase_admin.initialize_app(cred_obj)
DB = firestore.client()

def get_token():
	try:
		return open('.token', 'r').read()
	except FileNotFoundError:
		return os.getenv('BOT_TOKEN')

def get_report_chatid():
	try:
		return open('.report', 'r').read()
	except FileNotFoundError:
		return os.getenv('BOT_REPORT_CHATID')

bot = telebot.TeleBot(get_token())
# location = None
last_weather = None


@bot.message_handler(commands=["start"])
def command_start(message):
	# global location
	try:
		ref = DB.collection('locations').document(str(message.from_user.id)).get().to_dict()
		if message.date - ref['time'] > 3600:
			raise ValueError
		# location = ref['location']
		bot.send_message(message.chat.id, 'Данные о местоположении уже получены.\nИспользуйте "/weather", чтобы получить данные о погоде.')
	except (ValueError, TypeError):
		alert(f"[ ALERT ] in START_COMMAND of USER-{message.from_user.id} : time exceded (1 hour location cooldown) or user not exist.")
		keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
		button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
		keyboard.add(button_geo)
		bot.send_message(message.chat.id, "Необходимо дать доступ к местоположению.", reply_markup=keyboard)
	except:
		error(f"[ ERROR ] in COMMAND_START of USER-{message.from_user.id} : {sys.exc_info()[0]}.")
		


@bot.message_handler(content_types=["location"])
def save_location(message):
	# global location
	uid = str(message.from_user.id)
	try:
		ref = DB.collection('locations').document(uid)
		ref.update({
			'location'	:	{
				'latitude'	:	message.location.latitude,
				'longitude'	:	message.location.longitude
			},
			'time'	:	message.date
		})
	except:
		error(f"[ ERROR ] in SAVE_LOCATION of USER-{message.from_user.id} : {sys.exc_info()[0]}.")
		alert(f"[ ALERT ] in SAVE_LOCATION of USER-{message.from_user.id} : new user.")
		DB.collection('locations').document(uid).set({
			'user_id'	:	uid,
			'location'	:	{
				'latitude'	:	message.location.latitude,
				'longitude'	:	message.location.longitude
			},
			'time'			:	message.date
		})

	keyboard = types.ReplyKeyboardRemove()

	bot.send_message(message.chat.id, 'Данные получены.\nИспользуйте "/weather", чтобы получить данные о погоде.', reply_markup=keyboard)


@bot.message_handler(commands=['weather'])
def command_weather(message: types.Message):
	# global location
	msg = 'Необходимо дать доступ к местоположению командой "/start".'
	try:
		ref = DB.collection('locations').document(str(message.from_user.id)).get().to_dict()
		if message.date - ref['time'] > 3600:
			msg = 'Данные о местоположении устарели. Обновите командой "/start".'
			raise ValueError
		global last_weather
		location = ref['location']
		last_weather = get_weather(f"{location['latitude']},{location['longitude']}")
		bot.send_message(message.chat.id, text=f'{last_weather}\n\nЕсли произошла ошибка, отправьте отчёт командой "/report".')
	except ValueError:
		alert(f"[ ALERT ] in COMMAND_WEATHER of USER-{message.from_user.id} : time exceded (1 hour location cooldown).")
		bot.send_message(message.chat.id, text=msg)
	except TypeError:
		alert(f"[ ALERT ] in COMMAND_WEATHER of USER-{message.from_user.id} : user not exist.")
		bot.send_message(message.chat.id, text=msg)
	except:
		error(f"[ ERROR ] in COMMAND_WEATHER of USER-{message.from_user.id} : {sys.exc_info()[0]}.")
	# location = None


@bot.message_handler(commands=['weather_new'])
def command_weather_new(message: types.Message):
	# global location
	msg = 'Необходимо дать доступ к местоположению командой "/start".'
	try:
		ref = DB.collection('locations').document(str(message.from_user.id)).get().to_dict()
		if message.date - ref['time'] > 3600:
			msg = 'Данные о местоположении устарели. Обновите командой "/start".'
			raise ValueError
		global last_weather
		location = ref['location']
		last_weather = get_weather(f"{location['latitude']},{location['longitude']}")
		bot.send_message(message.chat.id, text=f'{last_weather}\n\nЕсли произошла ошибка, отправьте отчёт командой "/report".')
	except ValueError:
		alert(f"[ ALERT ] in COMMAND_WEATHER of USER-{message.from_user.id} : time exceded (1 hour location cooldown).")
		bot.send_message(message.chat.id, text=msg)
	except TypeError:
		alert(f"[ ALERT ] in COMMAND_WEATHER of USER-{message.from_user.id} : user not exist.")
		bot.send_message(message.chat.id, text=msg)
	except:
		error(f"[ ERROR ] in COMMAND_WEATHER of USER-{message.from_user.id} : {sys.exc_info()[0]}.")
	# location = None


@bot.message_handler(commands=['report'])
def command_report(message: types.Message):
	if last_weather != None:
		bot.send_message(get_report_chatid(), text=f'REPORT by {message.from_user.username} - {message.date}\n\n{last_weather}')
	bot.send_message(message.chat.id, text='Отчёт отправлен!')


@bot.message_handler(commands=['help'])
def command_help(message: types.Message):
	bot.send_message(message.chat.id, text='\
/start - Запустить бота.\n\
/help - Помощь.\n\
/weather - Получить погоду.\n\
/weather_new - Получить погоду в новой геолокации.')



print('------------------------')
print('/// BOT IS POLLING ///')
bot.polling()
