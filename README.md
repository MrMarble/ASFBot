# ASFBot

Telegram bot for [ArchiSteamFarm](https://github.com/JustArchi/ArchiSteamFarm)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

You need to have python3 installed in your system along with virtualenv and git.
```bash
sudo apt-get install python3

sudo apt-get install git

pip3 install virtualenv
```

### Installing

Clone the repository
```
git clone https://github.com/MrMarble/ASFBot.git 
```

Then lets make a virtual env to keep all the necessary files together

```
virtualenv ASFBot/
```
Now simply source into the virtualenv
```
source ASFBot/bin/activate

```
Install the requirements

```
pip install -r ASFBot/requirements.txt
```

And it sould be done


### Configuration

Explain what these tests test and why

```json
{
	"Telegram": {
		"language": "",
		"ignore": [],
		"TOKEN": "",
		"admin": []
	},
	"ASF": {
		"host": "",
		"port": ""
	}
}

```
1. Telegram:
    * language: Here you can config the language of the bot, at the moment only "es-ES" and "en-US" are available
    * ignore: This list will grow if someone that isn't in admin list talk to your bot
    * TOKEN: Here goes yout telegram api token, to get yours simply talk to @BotFather
    * admin: Here you can introduce the IDs of the users who can access the bot, you can leave it empty but anyone could control   your accounts!
2. ASF:
    * host: You need to put the ip of where ASF is running in server mode
    * port: The port where ASF is running in server mode
