# Eetlijst-Telegram-Bot
This Telegram bot daily reminds you to update your [Eetlijst.nl](https://eetlijst.nl/) status.

## Functions
It replies to direct messages and commands in groups.
Use the following commands:
- `/eetlijst`: Wie zijn ingeschreven?
- `/kok`: Wie moet koken?
- `/balans`: Verschuldigde bedrag p.p.
- `/kookpunten`: Kookpunten p.p.
- `/kookkosten`: Gemiddelde kookkosten p.p.
- `/verhouding`: Verhouding koken/eten p.p.

## Deployment
Create a new Telegram bot with the [BotFather](https://core.telegram.org/bots#6-botfather).

Then deploy at [Heroku](https://heroku.com/):
- Set buildpack to heroku/python
- Add config vars:
  - EETLIJST_USER: your [Eetlijst.nl](https://eetlijst.nl/) username
  - EETLIJST_PASS: your [Eetlijst.nl](https://eetlijst.nl/) password
  - GROUP_CHAT_ID: the id of your Telegram group chat to send a daily reminder
  - TELEGRAM_TOKEN: the token of the Telegram bot you just created (should look like: `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`)
  - TELEGRAM_DEV_ID: the Telegram user id of the owner of the bot (you?) for error messages (can be found by sending/forwarding a message to the [userinfobot](https://t.me/userinfobot))
  - Naam: 0123456789 (If you want personal daily reminders to set your Eetlijst status, add names (corresponding to your Eetlijst name) and Telegram user ids.)

![Eetlijstbot](Eetlijstbot.png)
