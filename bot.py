from datetime import time
from html import escape
from json import dumps
from logging import basicConfig, getLogger, INFO
from os import getenv
from pytz import timezone
from re import compile, search, IGNORECASE
from replies import *
from telegram import ChatAction, ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater, Dispatcher, JobQueue
from traceback import format_exception

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
if TELEGRAM_TOKEN is None:
    LookupError('Could not find TELEGRAM_TOKEN in config vars.')
TELEGRAM_DEV_ID = getenv('TELEGRAM_DEV_ID')
GROUP_CHAT_ID = getenv('GROUP_CHAT_ID')
if GROUP_CHAT_ID is None:
    LookupError('Could not find GROUP_CHAT_ID in config vars.')

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher
job_queue: JobQueue = updater.job_queue

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=INFO)
logger = getLogger(__name__)


def error_callback(update: object, context: CallbackContext):
    """Log the error and send a telegram message to notify the developer."""
    logger.error('Exception while handling an update:', exc_info=context.error)
    if isinstance(update, Update):
        if update.effective_message:
            text = ('Hallo. Er is helaas een fout opgetreden bij het verwerken van uw verzoek. '
                    'Mijn ontwikkelaar wordt op de hoogte gesteld.')
            update.effective_message.reply_text(text)
        update_str = update.to_dict()
    else:
        update_str = str(update)
    if TELEGRAM_DEV_ID is None:
        return
    tb_list = format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    text = (f'An exception was raised while handling an update\n'
            f'<pre>update = {escape(dumps(update_str, ensure_ascii=False, indent=2))}</pre>\n\n'
            f'<pre>context.chat_data = {escape(str(context.chat_data))}</pre>\n\n'
            f'<pre>context.user_data = {escape(str(context.user_data))}</pre>\n\n'
            f'<pre>{escape(tb_string)}</pre>')
    context.bot.send_message(TELEGRAM_DEV_ID, text, ParseMode.HTML)


def start_callback(update: Update, context: CallbackContext):
    """The callback function for the start command."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    context.bot.send_message(update.effective_chat.id, f'Hallo {update.effective_user.first_name}')


def balans_callback(update: Update, context: CallbackContext):
    """The callback function for the balans command."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    context.bot.send_message(update.effective_chat.id, balans(), ParseMode.HTML)


def eetlijst_callback(update: Update, context: CallbackContext):
    """The callback function for the eetlijst command."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    reply, persons = eetlijst()
    if str(update.effective_chat.id) == GROUP_CHAT_ID:
        for person in persons:
            context.job_queue.run_once(individual_callback, 0, person)
    context.bot.send_message(update.effective_chat.id, reply, ParseMode.HTML)


def individual_callback(context: CallbackContext):
    """The callback function for the individual messages."""
    person = context.job.context
    user_id = person.get_user_id()
    if user_id is not None:
        context.bot.send_chat_action(user_id, ChatAction.TYPING)
        text = f'{person}, je moet je nog inschrijven voor de maaltijd!\nJe kunt reageren in deze chat.'
        custom_keyboard = [['Ik eet mee🍔'], ['Ik eet niet mee🙅'], ['Ik kook🧑‍🍳']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        context.bot.send_message(user_id, text, ParseMode.HTML, reply_markup=reply_markup)


def kok_callback(update: Update, context: CallbackContext):
    """The callback function for the kok command."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    context.bot.send_message(update.effective_chat.id, kok(), ParseMode.HTML)


def kok_reminder_callback(context: CallbackContext):
    """The callback function for the kok reminder command."""
    cook = kok()
    if 'Er gaat nog niemand koken.' in cook:
        context.bot.send_chat_action(GROUP_CHAT_ID, ChatAction.TYPING)
        context.bot.send_message(GROUP_CHAT_ID, cook, ParseMode.HTML)


def kookkosten_callback(update: Update, context: CallbackContext):
    """The callback function for the kookkosten command."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    context.bot.send_message(update.effective_chat.id, kookkosten(), ParseMode.HTML)


def kookpunten_callback(update: Update, context: CallbackContext):
    """The callback function for the kookpunten command."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    context.bot.send_message(update.effective_chat.id, kookpunten(), ParseMode.HTML)


def personal_reminder_callback(context: CallbackContext):
    """The callback function for the personal reminder."""
    for person in eetlijst()[1]:
        context.job_queue.run_once(individual_callback, 0, person)


def public_reminder_callback(context: CallbackContext):
    """The callback function for the public reminder."""
    context.bot.send_chat_action(GROUP_CHAT_ID, ChatAction.TYPING)
    reply, persons = eetlijst()
    context.job_queue.run_once(kok_reminder_callback, 0)
    for person in persons:
        context.job_queue.run_once(individual_callback, 0, person)
    context.bot.send_message(GROUP_CHAT_ID, reply, ParseMode.HTML)


def verhouding_callback(update: Update, context: CallbackContext):
    """The callback function for the verhouding command."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    context.bot.send_message(update.effective_chat.id, verhouding(), ParseMode.HTML)


def cook_callback(update: Update, context: CallbackContext):
    """The callback function for the cook message."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    guests = search(r'\b(met)\b(.)* \d+', update.effective_message.text, IGNORECASE)
    if guests is not None:
        status = int(guests.group().split()[-1]) + 1
    else:
        status = 1
    context.bot.send_message(update.effective_chat.id, set_eetlijst(update.effective_user.id, status), ParseMode.HTML)


def eat_callback(update: Update, context: CallbackContext):
    """The callback function for the eat message."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    guests = search(r'\b(met)\b(.)* \d+', update.effective_message.text, IGNORECASE)
    if search('niet', update.effective_message.text, IGNORECASE) is not None:
        status = 0
    elif guests is not None:
        status = -1 * (int(guests.group().split()[-1]) + 1)
    else:
        status = -1
    context.bot.send_message(update.effective_chat.id, set_eetlijst(update.effective_user.id, status), ParseMode.HTML)


def unknown_callback(update: Update, context: CallbackContext):
    """The callback function for unknown commands."""
    context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    context.bot.send_message(update.effective_chat.id, 'Sorry, dat commando begreep ik niet.')


start_handler = CommandHandler('start', start_callback)
balans_handler = CommandHandler('balans', balans_callback)
eetlijst_handler = CommandHandler('eetlijst', eetlijst_callback)
kok_handler = CommandHandler('kok', kok_callback)
kookkosten_handler = CommandHandler('kookkosten', kookkosten_callback)
kookpunten_handler = CommandHandler('kookpunten', kookpunten_callback)
verhouding_handler = CommandHandler('verhouding', verhouding_callback)
cook_handler = MessageHandler(
    Filters.regex(compile(r'(?!.*\b(niet)\b)\b(ik)\b.+\b(kook|koken)\b', IGNORECASE)), cook_callback)
eat_handler = MessageHandler(
    Filters.regex(compile(r'\b(ik)\b.+(\b(eet)\b.+\b(mee)\b|\b(mee-eten|meeeten)\b)', IGNORECASE)), eat_callback)
unknown_handler = MessageHandler(Filters.command & Filters.chat_type.private, unknown_callback)

dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(balans_handler)
dispatcher.add_handler(eetlijst_handler)
dispatcher.add_handler(kok_handler)
dispatcher.add_handler(kookkosten_handler)
dispatcher.add_handler(kookpunten_handler)
dispatcher.add_handler(verhouding_handler)
dispatcher.add_handler(cook_handler)
dispatcher.add_handler(eat_handler)
# The unknown_handler must be added last.
dispatcher.add_handler(unknown_handler)

# Send daily personal reminder at 15h except on Sundays
job_queue.run_daily(personal_reminder_callback, time(hour=15, tzinfo=timezone('Europe/Amsterdam')), (0, 1, 2, 3, 4, 5))
# Send daily public reminder at 16h except on Sundays
job_queue.run_daily(public_reminder_callback, time(hour=16, tzinfo=timezone('Europe/Amsterdam')), (0, 1, 2, 3, 4, 5))

updater.start_polling()
updater.idle()
