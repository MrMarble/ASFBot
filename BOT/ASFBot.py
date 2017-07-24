#!/.ASFBot/bin/python
# -*- coding: utf-8 -*-
try:
	import sys
	import telebot	 #Library for telegram
	import requests	#Library for making requests to ASF
	import json	    #Library for parsing json documents
	import logging	 #Library for logs
	import re		#Regular expresions
	from telebot import types #For accessing the types more easyly
	from urllib.parse import quote  #To encode Text as URL
	from urllib.request import urlopen
	from datetime import datetime
except Exception as e:
	if '3.5' > sys.version[:3]:
		print("You need at least Python 3.5 and you are using %s,  please  upgrade"%sys.version[:3])
	else:
		print(e)
		print("Did you install the necessary libraries in requirements.txt?")
	sys.exit()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

try:
	config = json.load(open('config.json','r'))
	bot = telebot.TeleBot(config['Telegram']['TOKEN'])
	language = config['Telegram']['language']
	strings = json.load(open('strings.json', 'r'))
	strings = strings[language]
except Exception as e:
	logger.error(e)

def asf(cmd):
	try:
		server = 'http://%s:%s/IPC?command=%s'%(config['ASF']['host'], config['ASF']['port'], quote(cmd))
		response = urlopen(server)
		message = response.read().decode('utf-8')
		if '<p>' in message:
			return message.split('<p>')[1].split('</p>')[0].strip()
		else:
			return message
	except Exception as e:
		logger.error(e)

def is_admin(id):
	if len(config['Telegram']['admin']) == 0:
		return True
	if str(id) in config['Telegram']['admin']:
		return True
	return False

def main():
	try:
		bot.skip_pending=True
		bot.polling(none_stop=True)
	except Exception as e:
		logger.error(e)

'''*******************************************
		TELEGRAM BOT COMMANDS HANDLERS
*******************************************'''

@bot.message_handler(commands=['start'])
def start(message):
	if len(config['Telegram']['admin']) == 0:
		bot.send_message(message.chat.id, strings['1']%message.from_user.id, parse_mode='HTML', disable_web_page_preview=True)
	else:
		bot.send_message(message.chat.id, strings['2'], parse_mode='HTML', disable_web_page_preview=True)

@bot.message_handler(commands=['help'], func=lambda m: is_admin(m.from_user.id))
def help(message):
	bot.send_message(chat_id=message.chat.id, parse_mode="MARKDOWN", text=strings['3'])

@bot.message_handler(commands=['bots'], func= lambda m: is_admin(m.from_user.id))
def bots(message):
	status = json.loads(asf('api ASF'))
	for bot_name, bot_data in status['Bots'].items():
		playing = None
		current_cards_remaining = 0
		cards_remaining = 0

		if len(bot_data['CardsFarmer']['CurrentGamesFarming']) == 0:
			playing = strings['4']
		elif len(bot_data['CardsFarmer']['CurrentGamesFarming']) == 1:
			current_cards_remaining = bot_data['CardsFarmer']['CurrentGamesFarming'][0]['CardsRemaining']
			game_name = bot_data['CardsFarmer']['CurrentGamesFarming'][0]['GameName']
			playing = strings['5']%(game_name, current_cards_remaining)
		else:
			playing = strings['6']%len(bot_data['CardsFarmer']['CurrentGamesFarming'])
			game_name = bot_data['CardsFarmer']['CurrentGamesFarming'][0]['GameName']
			for game in bot_data['CardsFarmer']['CurrentGamesFarming']:
				current_cards_remaining = current_cards_remaining + game['CardsRemaining']

		if len(bot_data['CardsFarmer']['GamesToFarm']) > 0:
			for game in bot_data['CardsFarmer']['GamesToFarm']:
				cards_remaining = cards_remaining + game['CardsRemaining']

		bot.send_message(message.chat.id, strings['7']%(bot_name, playing, cards_remaining), parse_mode='MARKDOWN')

@bot.message_handler(commands=['list'], func= lambda m: is_admin(m.from_user.id))
def list(message):
	status = json.loads(asf('api ASF'))
	bots = ''
	for bot_name, bot_data in status['Bots'].items():
		if bot_data['BotConfig']['IsBotAccount']:
			bots = bots + '🤖 <b>%s</b> (%s) <code>%s</code>\n'%(bot_name, bot_data['BotConfig']['SteamLogin'],bot_data['SteamID']);
		else:
			bots = bots + '👑 <b>%s</b> (%s) <code>%s</code>\n'%(bot_name, bot_data['BotConfig']['SteamLogin'], bot_data['SteamID']);

	bot.send_message(message.chat.id, bots, parse_mode='HTML')

@bot.message_handler(commands=['status'], func= lambda m: is_admin(m.from_user.id))
def statuss(message):
	try:
		status = json.loads(asf('api ASF'))
		total_bots = 0
		farming_bots = 0
		games = 0
		cards_remaining = 0
		for bot_name, bot_data in status['Bots'].items():
			total_bots = total_bots + 1
			if len(bot_data['CardsFarmer']['CurrentGamesFarming']) > 0:
				farming_bots = farming_bots + 1
		status = asf('status ASF')
		games = re.findall('\d+',status.split('\n')[len(status.split('\n')) -1])[2]
		cards_remaining = re.findall('\d+',status.split('\n')[len(status.split('\n')) -1])[3]
		bot.send_message(message.chat.id,strings['8']%(farming_bots, total_bots, games, cards_remaining), parse_mode='MARKDOWN')
	except Exception as e:
		logger.error('[%s] /status: %s'%(datetime.now(), e))

@bot.message_handler(commands=['loot'], func= lambda m: is_admin(m.from_user.id))
def loot(message):
	try:
		msg = bot.send_message(message.chat.id,strings['9'])
		status = asf('loot ASF')
		bots = re.sub('[<>]', '*', status.strip())
		bot.edit_message_text(text=bots, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="MARKDOWN")
	except Exception as e:
		print('[%s] /loot: %s'%(datetime.now(), e))

@bot.message_handler(commands=['farm'], func= lambda m: is_admin(m.from_user.id))
def farm(message):
	try:
		bot.send_message(message.chat.id, srings["10"], parse_mode='MARKDOWN')
		status = asf('farm ASF')
		bot.edit_message_text(text=strings['11'], chat_id=message.chat.id, message_id=msg.message_id, parse_mode="MARKDOWN")
	except Exception as e:
		print('[%s] /farm: %s'%(datetime.now(), e))

'''*****************************************
	TELEGRAM CUSTOM COMMANDS HANDLERS
*****************************************'''

@bot.message_handler(func= lambda m: m.text[:4] ==  '!2fa' and is_admin(m.from_user.id))
def auth(message):
	cmd = message.text.split()[0]
	bot_name = message.text.split()[1]
	reply = asf('2fa %s'%bot_name)
	if 'Token' in reply:
		bot.reply_to(message=message, text='*%s*'%reply.split()[2], parse_mode="MARKDOWN")
	elif 'find' in reply:
		bot.reply_to(message=message, text=strings['12']%bot_name, parse_mode="MARKDOWN")
	else:
		bot.reply_to(message=message, text=strings['13'], parse_mode="MARKDOWN")

@bot.message_handler(func= lambda m: m.text[:5] == '!2fok' and is_admin(m.from_user.id))
def accept(message):
	cmd = message.text.split()[0]
	bot_name = message.text.split()[1]
	reply = re.sub('[<>]', '*',asf('2faok %s'%bot_name))
	bot.reply_to(message=message, text=reply, parse_mode="MARKDOWN")

@bot.message_handler(func= lambda m: m.text[:5] == '!2fno' and is_admin(m.from_user.id))
def deny(message):
	cmd = message.text.split()[0]
	bot_name = message.text.split()[1]
	reply = re.sub('[<>]', '*',asf('2fano %s'%bot_name))
	bot.reply_to(message=message, text=reply, parse_mode="MARKDOWN")

@bot.message_handler(func= lambda m: m.text[:11] == '!addlicense' and is_admin(m.from_user.id))
def license(message):
	cmd = message.text.split()[0]
	bot_name = message.text.split()[1]
	mensaje = message.text.split()[2]
	reply = re.sub('[<>]', '*',asf('addlicense %s %s'%(bot_name, mensaje))).strip()
	bot.reply_to(message=message, text=reply, parse_mode="MARKDOWN")

@bot.message_handler(func= lambda m: m.text[:5] == '!play' and is_admin(m.from_user.id))
def play(message):
	cmd = message.text.split()[0]
	bot_name = message.text.split()[1]
	mensaje = message.text.split()[2]
	reply = re.sub('[<>]', '*',asf('play %s %s'%(bot_name, mensaje))).strip()
	bot.reply_to(message=message, text=reply, parse_mode="MARKDOWN")

@bot.message_handler(func= lambda m: m.text[:6] == '!pause' and is_admin(m.from_user.id))
def pause(message):
	cmd = message.text.split()[0]
	bot_name = message.text.split()[1]
	reply = re.sub('[<>]', '*',asf('pause %s'%bot_name)).strip()
	bot.reply_to(message=message, text=reply, parse_mode="MARKDOWN")

@bot.message_handler(func= lambda m: m.text[:7] == '!resume' and is_admin(m.from_user.id))
def resume(message):
	cmd = message.text.split()[0]
	bot_name = message.text.split()[1]
	reply = re.sub('[<>]', '*',asf('resume %s'%bot_name)).strip()
	bot.reply_to(message=message, text=reply, parse_mode="MARKDOWN")

@bot.message_handler(func=lambda m: not is_admin(m.from_user.id))
def unknown(message):
	if not str(message.from_user.id) in config['Telegram']['ignore']:
		bot.send_message(config['Telegram']['admin'][0], strings['14']%(message.from_user.username, message.from_user.id,message.text))
		config['Telegram']['ignore'].append(str(message.from_user.id))
		json.dump(config, open('config.json', 'w'))
	bot.send_message(message.chat.id, strings['15'], parse_mode='HTML', disable_web_page_preview=True)

if __name__ == "__main__":	main()
