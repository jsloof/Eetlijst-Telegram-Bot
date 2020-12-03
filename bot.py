from telegram import ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
import datetime, logging, os, pytz, re, replies, sys, traceback

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_DEV_ID = os.environ['TELEGRAM_DEV_ID']
GROUP_CHAT_ID = os.environ['GROUP_CHAT_ID']

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def error_callback(update, context):
    """The callback function for erroneous commands."""
    # We want to notify the user of this problem. This will always work,
    # but not notify users if the update is callback or inline query, or a poll update.
    # In case you want this, keep in mind that sending the message could fail.
    if update.effective_message:
        text = 'Hallo. Er is helaas een fout opgetreden bij het verwerken van uw verzoek. ' \
               'Mijn ontwikkelaar wordt op de hoogte gesteld.'
        update.effective_message.reply_text(text)
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ''
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
    text = f'Hey.\nThe error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}</code>'
    # and send it to the dev
    context.bot.send_message(TELEGRAM_DEV_ID, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise

def start_callback(update, context):
    """The callback function for the start command."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hallo {update.effective_user.first_name}')

def eetlijst_callback(update, context):
    """The callback function for the eetlijst command."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    eetlijst = replies.eetlijst()
    if str(update.effective_chat.id) == GROUP_CHAT_ID:
        for person in eetlijst['unknown_persons']:
            context.job_queue.run_once(individual_callback, 0, context=person)
    context.bot.send_message(chat_id=update.effective_chat.id, text=eetlijst['reply'], parse_mode=ParseMode.HTML)

def individual_callback(context):
    """The callback function for the individual messages."""
    context.bot.send_chat_action(chat_id=context.job.context['telegram_id'], action=ChatAction.TYPING)
    context.bot.send_message(chat_id=context.job.context['telegram_id'], text=f'{context.job.context["name"]}, je moet je nog inschrijven op Eetlijst!\n' \
        'Je kunt reageren met <i>ik eet mee</i> of <i>ik eet niet mee</i>.', parse_mode=ParseMode.HTML)

def kok_callback(update, context):
    """The callback function for the kok command."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=replies.kok(), parse_mode=ParseMode.HTML)

def kookpunten_callback(update, context):
    """The callback function for the kookpunten command."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=replies.kookpunten(), parse_mode=ParseMode.HTML)

def kosten_callback(update, context):
    """The callback function for the kosten command."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=replies.kosten(), parse_mode=ParseMode.HTML)

def reminder_callback(context):
    """The callback function for the reminder."""
    context.bot.send_chat_action(chat_id=GROUP_CHAT_ID, action=ChatAction.TYPING)
    eetlijst = replies.eetlijst()
    for person in eetlijst['unknown_persons']:
        context.job_queue.run_once(individual_callback, 0, context=person)
    context.bot.send_message(chat_id=GROUP_CHAT_ID, text=eetlijst['reply'], parse_mode=ParseMode.HTML)

def verhouding_callback(update, context):
    """The callback function for the verhouding command."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=replies.verhouding(), parse_mode=ParseMode.HTML)

def cook_callback(update, context):
    """The callback function for the cook message."""
    if 'niet' not in update.message.text.split():
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text=replies.set_eetlijst(update.effective_user.id, 1), parse_mode=ParseMode.HTML)

def eat_callback(update, context):
    """The callback function for the eat message."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    status = 0 if 'niet' in update.message.text.split() else -1
    context.bot.send_message(chat_id=update.effective_chat.id, text=replies.set_eetlijst(update.effective_user.id, status), parse_mode=ParseMode.HTML)

def unknown_callback(update, context):
    """The callback function for unknown commands."""
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, dat commando begreep ik niet.')

start_handler = CommandHandler('start', start_callback)
eetlijst_handler = CommandHandler('eetlijst', eetlijst_callback)
kok_handler = CommandHandler('kok', kok_callback)
kookpunten_handler = CommandHandler('kookpunten', kookpunten_callback)
kosten_handler = CommandHandler('kosten', kosten_callback)
verhouding_handler = CommandHandler('verhouding', verhouding_callback)
cook_handler = MessageHandler(Filters.regex(re.compile(r'(ik).+(kook|koken)', re.IGNORECASE)), cook_callback)
eat_handler = MessageHandler(Filters.regex(re.compile(r'(ik).+((eet).+(mee)|(mee-eten|meeeten))', re.IGNORECASE)), eat_callback)
unknown_handler = MessageHandler(Filters.command, unknown_callback)

dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(eetlijst_handler)
dispatcher.add_handler(kok_handler)
dispatcher.add_handler(kookpunten_handler)
dispatcher.add_handler(kosten_handler)
dispatcher.add_handler(verhouding_handler)
dispatcher.add_handler(cook_handler)
dispatcher.add_handler(eat_handler)
# The unknown_handler must be added last.
dispatcher.add_handler(unknown_handler)

job_queue.run_daily(reminder_callback, datetime.time(hour=15, tzinfo=pytz.timezone('Europe/Amsterdam')))

updater.start_polling()
updater.idle()
