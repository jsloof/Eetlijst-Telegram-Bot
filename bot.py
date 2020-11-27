from telegram import ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.utils.helpers import mention_html
import logging, os, sys, traceback

from bs4 import BeautifulSoup
import requests, re

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
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    ps = Parser()
    reply = ""
    if ps.get_eetlijst()[1] != []:
        reply += str(ps.get_eetlijst()[1]) + " gaat koken.\n"
    if ps.get_eetlijst()[0] != []:
        reply += str(ps.get_eetlijst()[0]) + " eten mee.\n"
    if ps.get_eetlijst()[3] != []:
        reply += str(ps.get_eetlijst()[3]) + " moeten zich nog inschrijven."
    update.message.reply_text(reply)

def kok_callback(update, context):
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    ps = Parser()
    if ps.get_eetlijst()[1] != []:
        reply = str(ps.get_eetlijst()[1]) + " gaat koken."
    else:
        reply = "Wie wil er koken?"
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

def kookpunten_callback(update, context):
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    update.message.reply_text(f'p{kookpunten()}')

def kosten_callback(update, context):
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    update.message.reply_text(f'k{kosten()}')

def verhouding_callback(update, context):
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply, parse_mode=ParseMode.HTML)
    update.message.reply_text(f'v{verhouding()}')

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
    reply = zipped.replace('{\'','<b>Verhouding koken/eten:</b>\n<code>').replace('\': \'','</code> (').replace('\', \'',')\n<code>').replace('\'}',')')
    return reply

class Parser:

    def __init__(self):
        self.EETLIJST_USER = os.environ['EETLIJST_USER']
        self.EETLIJST_PASS = os.environ['EETLIJST_PASS']

        self.login_url = 'http://eetlijst.nl/login.php'
        self.values = {'login': self.EETLIJST_USER, 'pass': self.EETLIJST_PASS}

        self.main_page = requests.post(self.login_url, data=self.values)
        self.soup_main_page = BeautifulSoup(self.main_page.content, "lxml")

        self.kosten_url = self.soup_main_page.find_all('a')[2]['href']
        self.session_id = re.split('\W', self.kosten_url)[-1]

        self.kosten_page = requests.get('http://eetlijst.nl/' + self.kosten_url)
        self.soup_kosten_site = BeautifulSoup(self.kosten_page.content, "lxml")

        self.today_status = self.soup_main_page.find_all('td', class_='r')

    # Get the eetlijst of today
    def get_eetlijst(self):
        eat, cook, absent, unknown = [], [], [], []
        list_images = self.today_status[1].parent.find_all('img')
        for image in list_images:
            choice = image['src']
            person = re.split('\s', image['title'])[0]
            if choice == 'eet.gif':
                eat.append(person)
            elif choice == 'kook.gif':
                cook.append(person)
            elif choice == 'nop.gif':
                absent.append(person)
            else:
                unknown.append(person)
        return eat, cook, absent, unknown

    # Returns an array with the eaters
    def get_eaters(self):
        return self.get_eetlijst()[0]

    # Returns an array with the cook(s)
    def get_cook(self):
        return self.get_eetlijst()[1]

    # Returns an array with the absent persons
    def get_absent(self):
        return self.get_eetlijst()[2]

    # Returns an array with the persons with unknown status
    def get_unknown(self):
        return self.get_eetlijst()[3]

    # Get the ratio cook/eat
    def get_ratio(self, person: int = None):
        list_ratio = []
        all_times_cook = self.soup_kosten_site.find('td', text='  Aantal keer gekookt').parent.find_all('td', class_="r")
        all_times_eat = self.soup_kosten_site.find('td', text='  Aantal keer meegegeten').parent.find_all('td', class_="r")
        for i in range(len(all_times_cook)):
            times_cook = int(all_times_cook[i].text)
            times_eat = int(all_times_eat[i].text)
            list_ratio.append(round(times_cook / times_eat, 3))
        return list_ratio if person == None else list_ratio[person]

    # Get the costs
    def get_costs(self, person: int = None):
        list_costs = []
        all_costs = self.soup_kosten_site.find('td', text='  Kookt gemiddeld voor (p.p.)').parent.find_all('td', class_="r")[0:-1]
        for i in range(len(all_costs)):
            costs = float(all_costs[i].text.replace(',','.'))
            list_costs.append(round(costs, 2))
        return list_costs if person == None else list_costs[person]

    # Get the names
    def get_names(self, person: int = None):
        list_names = []
        all_names = self.soup_kosten_site.find('th', colspan='3').parent.find_all('th')[1:-1]
        for i in range(len(all_names)):
            list_names.append(all_names[i].text)
        return list_names if person == None else list_names[person]

    #Get the cooking points
    def get_points(self, person: int = None):
        list_points = []
        all_points = self.soup_kosten_site.find_all('td', class_="l", colspan='3')[-1].parent.find_all('td', class_="r")[0:-1]
        for i in range(len(all_points)):
            list_points.append(all_points[i].text)
        return list_points if person == None else list_points[person]

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
