# Eetlijst-Telegram-Bot
This Telegram bot daily reminds you to update your [Eetlijst.nl](https://eetlijst.nl/) status.

## Functions
It replies to direct messages and commands in groups.
Use the following commands:
- `/eetlijst`: Check wie er zijn ingeschreven
- `/kok`: Check wie er moet koken
- `/kookpunten`: Check kookpunten
- `/kosten`: Check gemiddelde kosten
- `/verhouding`: Check verhouding koken/eten

## Deployment
Create a new Telegram bot with the [BotFather](https://core.telegram.org/bots#6-botfather).

Then deploy at [Heroku](https://heroku.com/):
- Set buildpack to heroku/python
- Add config vars:
  - EETLIJST_USER: your [Eetlijst.nl](https://eetlijst.nl/) username
  - EETLIJST_PASS: your [Eetlijst.nl](https://eetlijst.nl/) password
  - TELEGRAM_DEV_ID: your Telegram user id for error messages (can be found here: [userinfobot](https://t.me/userinfobot))
  - TELEGRAM_TOKEN: your Telegram bot token (should look like: `1234567890:abcd_efgh_qwertyuiopASDFGHJKLzxcvbn`)
  
![Eetlijstbot](Eetlijstbot.png)
