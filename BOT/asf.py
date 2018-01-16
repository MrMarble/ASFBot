import requests


class Asf():
    """ASF Wrapper for the api
    """

    def __init__(self, ip, port):
        """ASF wrapper for the api
        
        Arguments:
            ip {string} -- IP where ASF is located
            port {int} -- Port where ASF is listening
        """
        self.ip = ip
        self.port = port

    def send_command(self, cmd):
        """Function for sending commands to ASF
        
        Arguments:
            cmd {string} -- Command to send
        
        Returns:
            [json] -- Response of ASF Api
        """

        end_point = 'http://%s:%s/Api/Command/%s'%(self.ip, self.port, cmd)
        response = requests.post(end_point)
        return response.json()['Result']

    def get_bot(self, bot_names):
        """Function for accesing bot instances of ASF
        
        Arguments:
            bot_names {string}{array} -- Name of the bot to get retrieved, it also can be an array
        
        Returns:
            json -- Response of ASF Api
        """

        bots = ''
        if isinstance(bot_names, list):
            bots = ','.join(bot_names)
        else:
            bots = bot_names

        end_point = 'http://%s:%s/Api/Bot/%s'%(self.ip, self.port, bots)
        response = requests.get(end_point)
        return response.json()['Result']
