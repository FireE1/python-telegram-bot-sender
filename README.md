# python-telegram-bot-sender
If you need to send media files to your telegram channel every 30 minutes from 7 a.m to 1 a.m, this script can do it. It uses '[aiogram](https://aiogram.dev/)' python lib, calculate time and have simple .json file to operate.

## Usage:
- Create a directory/folder 'media' in the same directory/folder where the script is located.
- Create a bot through the Telegram bot '[BotFather](https://core.telegram.org/bots/tutorial)' and receive a personal token for your bot. Or, if you already have a bot, get its token.
- Get your personal ID as a nine-digit number.
  Optional: Get the personal ID of the people you want to connect to the bot (they will only be able to check the number of remaining media)*.
- Get the name of your Telegram channel.
- Input all the info you receive into a [.json file](./data.json).
- Make your bot join your channel.
- Start the [script](./bot_script.py).
- Now you can start sending media to the bot or simply place them in the 'media' directory/folder and the bot will start sending media every 30 minutes.

## Startup requirements:
- Python 3.11 +
- [aiogram](https://aiogram.dev/) 3.3.0

## Might be helpful:
[Python virtual environment](https://docs.python.org/3/library/venv.html)
