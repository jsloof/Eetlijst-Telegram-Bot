from parser import Parser
from telegram import ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.utils.helpers import mention_html
import logging, os, sys, traceback

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_DEV_ID = os.environ['TELEGRAM_DEV_ID']

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start_callback(update, context):
    update.message.reply_text(f'Hallo {update.effective_user.first_name}')

def error_callback(update, context):
    # we want to notify the user of this problem. This will always work, but not notify users if the update is an
    # callback or inline query, or a poll update. In case you want this, keep in mind that sending the message
    # could fail
    if update.effective_message:
        text = "Hallo. Er is helaas een fout opgetreden bij het verwerken van uw verzoek. " \
               "Mijn ontwikkelaar wordt op de hoogte gesteld."
        update.effective_message.reply_text(text)
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""
    # normally, we always have an user. If not, its either a channel or a poll update.
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\nThe error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
           f"</code>"
    # and send it to the dev
    context.bot.send_message(TELEGRAM_DEV_ID, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise

def eetlijst_callback(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=eetlijst(), parse_mode=ParseMode.HTML)

def kok_callback(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    update.message.reply_text(kok())

def kookpunten_callback(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=kookpunten(), parse_mode=ParseMode.HTML)

def kosten_callback(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=kosten(), parse_mode=ParseMode.HTML)

def verhouding_callback(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=verhouding(), parse_mode=ParseMode.HTML)

def schreeuw_callback(update, context):
    if update.message.text == update.message.text.upper():
        update.message.reply_text('JE HOEFT NIET ZO TE SCHREEUWEN!!1')

def unknown_callback(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, dat commando begreep ik niet.")

def eetlijst():
    ps = Parser()
    reply = ""
    if ps.get_eetlijst()[1] != []:
        reply += str(ps.get_eetlijst()[1]) + " gaat koken.\n"
    if ps.get_eetlijst()[0] != []:
        reply += str(ps.get_eetlijst()[0]) + " eten mee.\n"
    if ps.get_eetlijst()[3] != []:
        reply += str(ps.get_eetlijst()[3]) + " moeten zich nog inschrijven."
    return reply

def kok():
    ps = Parser()
    if ps.get_eetlijst()[1] != []:
        reply = str(ps.get_eetlijst()[1]) + " gaat koken."
    else:
        reply = "Wie wil er koken?"
    return reply

def kookpunten():
    ps = Parser()
    zipped = str(dict(zip(ps.get_points(), ps.get_names())))
    reply = zipped.replace('{\'','<b>Kookpunten:</b>\n<code>').replace('\': \'','</code> (').replace('\', \'',')\n<code>').replace('\'}',')')
    return reply

def kosten():
    ps = Parser()
    zipped = str(dict(zip(ps.get_costs(), ps.get_names())))
    reply = zipped.replace('{\'','<b>Gemiddelde kosten:</b>\n<code>€').replace('\': \'','</code> (').replace('\', \'',')\n<code>€').replace('\'}',')')
    return reply

def verhouding():
    ps = Parser()
    zipped = str(dict(zip(ps.get_ratio(), ps.get_names())))
    reply = zipped.replace('{','<b>Verhouding koken/eten:</b>\n<code>').replace(': \'','</code> (').replace('\', ',')\n<code>').replace('\'}',')')
    return reply

start_handler = CommandHandler('start', start_callback)
eetlijst_handler = CommandHandler('eetlijst', eetlijst_callback)
kok_handler = CommandHandler('kok', kok_callback)
kookpunten_handler = CommandHandler('kookpunten', kookpunten_callback)
kosten_handler = CommandHandler('kosten', kosten_callback)
verhouding_handler = CommandHandler('verhouding', verhouding_callback)
schreeuw_handler = MessageHandler(Filters.text & (~Filters.command), schreeuw_callback)
unknown_handler = MessageHandler(Filters.command, unknown_callback)

dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(eetlijst_handler)
dispatcher.add_handler(kok_handler)
dispatcher.add_handler(kookpunten_handler)
dispatcher.add_handler(kosten_handler)
dispatcher.add_handler(verhouding_handler)
dispatcher.add_handler(schreeuw_handler)
dispatcher.add_handler(unknown_handler) # This handler must be added last

updater.start_polling()
updater.idle()
