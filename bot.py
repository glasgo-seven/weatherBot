#!/usr/bin/env python
# coding: utf-8

import codecs
import os
from random import randint
from time import time, sleep, strftime, localtime
import sys

import telebot
from telebot import types

from alert import *
from weather import get_weather
from db import data, Data

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
		bot.send_message(message.chat.id, text="Нажми на кнопку внизу, чтобы получить погоду в твоей геопозиции!", reply_markup=keyboard)
	except:
		error(f"[ ERROR ] in COMMAND_START of USER-{message.from_user.id} : {sys.exc_info()}")


@bot.message_handler(content_types=["location"])
def save_location(message):
	try:
		uid_i = message.from_user.id
		uid = str(uid_i)
		location = f"{message.location.latitude},{message.location.longitude}"
		bot_msg = bot.send_message(message.chat.id, text='Загружаю погоду...')
		weather = get_weather(message, location)

		user = Data.query.get(uid_i)
		if user == None:
			data.session.add(Data(uid=uid_i, username=message.from_user.username, time=message.date, weather=weather))
			data.session.commit()
		else:
			user.username = message.from_user.username
			user.time = message.date
			user.weather = weather
			data.session.commit()

		bot.edit_message_text(chat_id=message.chat.id, message_id=bot_msg.message_id, text=f'{weather}\n\nЗаметили ошибку?\nОтправьте отчёт командой "/report"!')
	except:
		error(f"[ ERROR ] in SAVE_LOCATION of USER-{message.from_user.id} : {sys.exc_info()}")


@bot.message_handler(commands=['report'])
def command_report(message: types.Message):
	try:
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		keyboard.add(
			types.InlineKeyboardButton(text="Пустой прогноз", callback_data='empty_answer'),
			types.InlineKeyboardButton(text="Неверная погода", callback_data='wrong_weather'),
			types.InlineKeyboardButton(text="Сбой языка", callback_data='language_error'),
			types.InlineKeyboardButton(text="Другое", callback_data='other')
		)
		bot.send_message(message.chat.id, text="Выбери тип ошибки:", reply_markup=keyboard)
	except:
		error(f"[ ERROR ] in COMMAND_REPORT of USER-{message.from_user.id} : {sys.exc_info()}")


def get_rid(l = 5):
	from secrets import token_hex
	return token_hex(l)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	try:
		if call.message:
			uid_i = call.from_user.id
			user = Data.query.get(uid_i)
			if user != None:
				rid = get_rid()
				bot.send_message(get_report_chatid(), text=f'----------------\nREPORT {rid}\ntype\n⠀[{call.data.upper()}]\nby\n⠀username⠀:⠀{user.username}\n⠀user_id⠀:⠀{user.uid}\n⠀date⠀:⠀{strftime("%d-%m-%y %H:%M:%S", localtime(user.time))} (e{user.time})\n----------------\n\n{user.weather}')
				bot.send_message(call.message.chat.id, text=f'Отчёт об ошибке отправлен!\nRID:⠀{rid}')
			else:
				bot.send_message(call.message.chat.id, text='К сожалению, отчёт не может быть отправлен.')
	except:
		error(f"[ ERROR ] in CALLBACK_INLINE of USER-{call.message.from_user.id} : {sys.exc_info()}")


@bot.message_handler(commands=['report_callback'])
def command_report_callback(message: types.Message):
	try:
		uid, rid, msg = message.text.split('\n')[1:]
		bot.send_message(message.chat.id, text=f"❗ Ответ на ваш отчёт ❗\n✔️ RID: {rid} !\n\n{msg}\n⠀by {message.from_user.username}")
	except:
		error(f"[ ERROR ] in COMMAND_REPORT_CALLBACK of USER-{message.from_user.id} : {sys.exc_info()}")


print('------------------------')
print('/// DATA ///')
print(Data.query.all())
print('/// BOT IS POLLING ///')
bot.polling()
