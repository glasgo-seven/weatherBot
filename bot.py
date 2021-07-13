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
last_weather = None


@bot.message_handler(commands=["start"])
def command_start(message):
	try:
		keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True) #, one_time_keyboard=True)
		button_geo = types.KeyboardButton(text="Получить погоду!", request_location=True)
		keyboard.add(button_geo)
		bot.send_message(message.chat.id, "Нажми на кнопку внизу, чтобы получить погоду в твоей геопозиции!", reply_markup=keyboard)
	except:
		error(f"[ ERROR ] in COMMAND_START of USER-{message.from_user.id} : {sys.exc_info()}")


@bot.message_handler(content_types=["location"])
def save_location(message):
	try:
		uid = str(message.from_user.id)
		global last_weather
		location = f"{message.location.latitude},{message.location.longitude}"
		bot_msg = bot.send_message(message.chat.id, text='Загружаю погоду...')
		last_weather = get_weather(message, location)
		bot.edit_message_text(chat_id=message.chat.id, message_id=bot_msg.message_id, text=f'{last_weather}\n\nЕсли произошла ошибка, отправьте отчёт командой "/report".')
	except:
		error(f"[ ERROR ] in SAVE_LOCATION of USER-{message.from_user.id} : {sys.exc_info()}")


@bot.message_handler(commands=['report'])
def command_report(message: types.Message):
	try:
		if last_weather != None:
			bot.send_message(get_report_chatid(), text=f'REPORT by\n⠀username⠀:⠀{message.from_user.username}\n⠀user_id⠀:⠀{message.from_user.id}\n⠀date⠀:⠀{message.date}\n\n{last_weather}')
		bot.send_message(message.chat.id, text='Отчёт отправлен!')
	except:
		error(f"[ ERROR ] in COMMAND_REPORT of USER-{message.from_user.id} : {sys.exc_info()}")


print('------------------------')
print('/// BOT IS POLLING ///')
bot.polling()
