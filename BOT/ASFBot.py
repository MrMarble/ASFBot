#!/.ASFBot/bin/python
# -*- coding: utf-8 -*-

try:
    import sys
    import logging
    import telebot
    from telebot import types
    import re
    import json
    import asf
except Exception as e:
    if '3.5' > sys.version[:3]:
        print('You need at least Python 3.5 and you are using %s, please upgrade'%sys.version[:3])
    else:
        print(e)
        print('Did you install the necessary libraries in requirements.txt?')
    sys.exit()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
try:
    config = json.load(open('config.json', 'r'))
    strings = json.load(open('strings.json',mode='r',encoding="utf-8"))['es-ES']
    asf = asf.Asf(config['ASF']['host'], config['ASF']['port'])
    bot = telebot.TeleBot(config['Telegram']['TOKEN'],skip_pending=True)
except Exception as e:
    logger.error(e)
    sys.exit()

def main():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(e)
        sys.exit()

def commands_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton('list'), types.KeyboardButton('bots'), types.KeyboardButton('status'), types.KeyboardButton('!2fa'),  types.KeyboardButton('!2faok'), types.KeyboardButton('!2fano'), types.KeyboardButton('!addlicense'))
    return keyboard

@bot.message_handler(commands=['start'])
def command_start(message):
        bot.send_message(message.chat.id, strings['start']['admins'], reply_markup=commands_keyboard(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == 'list')
def command_list(msg):
    logger.info('Comando recibido')
    asf_bots = asf.get_bot('ASF')
    enabled = ''
    disabled = ''
    for bot_instance in asf_bots:
        if bot_instance['SteamID'] is not 0:
            if bot_instance['BotConfig']['IsBotAccount']:
                enabled += strings['list']['isbot']%(bot_instance['BotName'], bot_instance['SteamID']) + '\n'
            else:
                enabled += strings['list']['nobot']%(bot_instance['BotName'], bot_instance['SteamID']) + '\n'
        else:
                disabled += strings['list']['disabled']%(bot_instance['BotName']) + '\n'

    bot.send_message(msg.chat.id, enabled, parse_mode='HTML')
    if disabled:
        bot.send_message(msg.chat.id, disabled, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == 'bots')
def command_bots(msg):
    logger.info('Comando recibido')
    asf_bots = asf.get_bot('ASF')
    for bot_instance in asf_bots:
        if bot_instance['SteamID'] is not 0:
            playing = None
            current_cards_remaining = 0
            cards_remaining = 0
            bot_name = bot_instance['BotName']
            if not bot_instance['CardsFarmer']['CurrentGamesFarming']:
                playing = strings['bots']['nogames']
            elif len(bot_instance['CardsFarmer']['CurrentGamesFarming']) == 1:
                current_cards_remaining = bot_instance['CardsFarmer']['CurrentGamesFarming'][0]['CardsRemaining']
                game_name = bot_instance['CardsFarmer']['CurrentGamesFarming'][0]['GameName']
                playing = strings['bots']['onegame']%(game_name, current_cards_remaining)
            else:
                playing = strings['bots']['games']%len(bot_instance['CardsFarmer']['CurrentGamesFarming'])
                for game in bot_instance['CardsFarmer']['CurrentGamesFarming']:
                    current_cards_remaining = current_cards_remaining + game['CardsRemaining']

            if bot_instance['CardsFarmer']['GamesToFarm']:
                for game in bot_instance['CardsFarmer']['GamesToFarm']:
                    cards_remaining = cards_remaining + game['CardsRemaining']

            bot.send_message(msg.chat.id, strings['bots']['message']%(bot_name, playing, cards_remaining), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == 'status')
def command_status(msg):
    try:
        asf_bots = asf.get_bot('ASF')
        total_bots = 0
        farming_bots = 0
        games = 0
        cards_remaining = 0
        for bot_instance in asf_bots:
            total_bots += 1
            if bot_instance['CardsFarmer']['CurrentGamesFarming']:
                farming_bots = farming_bots + 1
        status = asf.send_command('status ASF')
        games = re.findall(r'\d+', status.split('\n')[len(status.split('\n')) -1])[2]
        cards_remaining = re.findall(r'\d+', status.split('\n')[len(status.split('\n')) -1])[3]
        bot.send_message(msg.chat.id, strings['status']['message']%(farming_bots, total_bots, games, cards_remaining), parse_mode='HTML')
    except Exception as e:
        logger.error('/status: %s'%e)

@bot.message_handler(func=lambda m: m.text == '!2fa')
def command_FA(msg):
    try:
        asf_bots = asf.get_bot('ASF')
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        for bot_instance  in asf_bots:
            buttons.append(types.InlineKeyboardButton(bot_instance['BotName'], callback_data='!2fa %s'%bot_instance['BotName']))
        keyboard.add(*buttons)
        bot.send_message(msg.chat.id, strings['2FA']['select'], reply_markup=keyboard)
    except Exception as e:
        logger.error('2FA: %s'%e)

@bot.callback_query_handler(lambda q: '!2fa ' in q.data)
def query_FA(q):
    try:
        asf_FA = asf.send_command('2fa %s'%q.data[3:])
        asf_bot = re.search(r"<(.*)>", asf_FA).group(1)
        asf_code = re.search(r" [A-Z0-9]{4,6}$", asf_FA).group(0).lstrip()
        bot.answer_callback_query(q.id)
        bot.reply_to(q.message, strings['2FA']['code']%(asf_bot, asf_code),parse_mode='HTML', reply_markup=commands_keyboard())
    except Exception as e:
        logger.error('2FA: %s'%e)
        bot.reply_to(q.message, strings['2FA']['error']%asf_bot, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == '!2faok')
def command_FAOK(msg):
    try:
        asf_bots = asf.get_bot('ASF')
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        for bot_instance  in asf_bots:
            buttons.append(types.InlineKeyboardButton(bot_instance['BotName'], callback_data='!2faok %s'%bot_instance['BotName']))
        keyboard.add(*buttons)
        bot.send_message(msg.chat.id, strings['2FAOK']['message'], reply_markup=keyboard)

    except Exception as e:
        logger.error('2FA-OK: %s'%e)

@bot.callback_query_handler(lambda q: '!2faok ' in q.data)
def query_FAOK(q):
    try:
        asf_FA = asf.send_command('2faok %s'%q.data[5:])
        asf_bot = re.search(r"<(.*)>", asf_FA).group(1)
        asf_ans = re.search(r">(.*)", asf_FA).group(1).lstrip()
        logger.info(asf_FA)
        bot.answer_callback_query(q.id)
        bot.reply_to(q.message, strings['2FAOK']['reply']%(asf_bot, asf_ans),parse_mode='HTML', reply_markup=commands_keyboard())
    except Exception as e:
        logger.error('2FA-OK: %s'%e)
        bot.reply_to(q.message, strings['2FAOK']['reply']%(asf_bot, asf_ans),parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == '!2fano')
def command_FANO(msg):
    try:
        asf_bots = asf.get_bot('ASF')
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        for bot_instance  in asf_bots:
            buttons.append(types.InlineKeyboardButton(bot_instance['BotName'], callback_data='!2fano %s'%bot_instance['BotName']))
        keyboard.add(*buttons)
        bot.send_message(msg.chat.id, strings['2FAOK']['message'], reply_markup=keyboard)

    except Exception as e:
        logger.error('2FA-OK: %s'%e)

@bot.callback_query_handler(lambda q: '!2fano ' in q.data)
def query_FANO(q):
    try:
        asf_FA = asf.send_command('2fano %s'%q.data[5:])
        asf_bot = re.search(r"<(.*)>", asf_FA).group(1)
        asf_ans = re.search(r">(.*)", asf_FA).group(1).lstrip()
        logger.info(asf_FA)
        bot.answer_callback_query(q.id)
        bot.reply_to(q.message, strings['2FAOK']['reply']%(asf_bot, asf_ans),parse_mode='HTML', reply_markup=commands_keyboard())
    except Exception as e:
        logger.error('2FA-NO: %s'%e)
        bot.reply_to(q.message, strings['2FAOK']['reply']%(asf_bot, asf_ans),parse_mode='HTML')

@bot.message_handler(func= lambda m: m.text == '!addlicense')
def command_addlic(msg):
    try:
        bot.send_message(msg.chat.id,strings['addlicense']['message'], reply_markup=types.ForceReply())
    except Exception as e:
        logger.error('addlicense: %s'%e)

def addlicense(id, license):
    if re.match(r"^\d+$", license):
        asf_license = asf.send_command('addlicense ASF %s'%license)
        reply = re.sub(r"<(.*)>(.*)",r"<b>\1</b> \2",asf_license)
        logger.info(reply)
        bot.send_message(id, reply, parse_mode='HTML')


@bot.message_handler(func=lambda m: True)
def message(msg):
    if msg.reply_to_message:
        if strings['addlicense']['message'] == msg.reply_to_message.text:
            addlicense(msg.chat.id, msg.text)
    else:        
        asf_command = asf.send_command(msg.text)
        bot.send_message(msg.chat.id,asf_command)

if __name__ == '__main__':
    main()
