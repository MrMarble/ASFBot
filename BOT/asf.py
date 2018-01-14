import requests


class Asf():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_command(self, cmd):
        end_point = 'http://%s:%s/Api/Command/%s'%(self.ip, self.port, cmd)
        response = requests.post(end_point)
        return response.json()['Result']

    def get_bot(self, bot_names):
        bots = ''
        if isinstance(bot_names, list):
            bots = ','.join(bot_names)
        else:
            bots = bot_names

        end_point = 'http://%s:%s/Api/Bot/%s'%(self.ip, self.port, bots)
        response = requests.get(end_point)
        return response.json()['Result']
