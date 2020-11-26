from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import replies as rp
import os, logging

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    update.message.reply_text(f'Hallo {update.effective_user.first_name}')

#def eetlijst(update, context):
#    update.message.reply_text(f'{rp.eetlijst()}')
#
#def kok(update, context):
#    update.message.reply_text(f'{rp.kok()}')
#
#def kookpunten(update, context):
#    update.message.reply_text(f'{rp.kookpunten()}')
#
#def kosten(update, context):
#    update.message.reply_text(f'{rp.kosten()}')
#
#def verhouding(update, context):
#    update.message.reply_text(f'{rp.verhouding()}')

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, dat commando begreep ik niet.")

start_handler = CommandHandler('start', start)
#eetlijst_handler = CommandHandler('eetlijst', eetlijst)
#kok_handler = CommandHandler('kok', kok)
#kookpunten_handler = CommandHandler('kookpunten', kookpunten)
#kosten_handler = CommandHandler('kosten', kosten)
#verhouding_handler = CommandHandler('verhouding', verhouding)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(start_handler)
#dispatcher.add_handler(eetlijst_handler)
#dispatcher.add_handler(kok_handler)
#dispatcher.add_handler(kookpunten_handler)
#dispatcher.add_handler(kosten_handler)
#dispatcher.add_handler(verhouding_handler)
dispatcher.add_handler(unknown_handler) # This handler must be added last

updater.start_polling()
updater.idle()
