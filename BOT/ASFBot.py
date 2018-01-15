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


@bot.message_handler(commands=['start'])
def command_start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton('list'), types.KeyboardButton('bots'), types.KeyboardButton('status'))
    bot.send_message(message.chat.id, strings['start']['admins'], reply_markup=keyboard)

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

@bot.message_handler(func=lambda m: True)
def message(msg):
    asf_command = asf.send_command(msg.text)
    bot.send_message(msg.chat.id,asf_command)

if __name__ == '__main__':
    main()
