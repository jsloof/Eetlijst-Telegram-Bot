from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os, logging

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    update.message.reply_text(f'Hallo {update.effective_user.first_name}')

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, dat commando begreep ik niet.")

start_handler = CommandHandler('start', start)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(unknown_handler) # This handler must be added last

updater.start_polling()
updater.idle()
