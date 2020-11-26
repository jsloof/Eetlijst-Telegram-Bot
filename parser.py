from bs4 import BeautifulSoup
import requests, re, os

EETLIJST_USER = os.environ['EETLIJST_USER']
EETLIJST_PASS = os.environ['EETLIJST_PASS']

login_url = 'http://eetlijst.nl/login.php'
values = {'login': EETLIJST_USER, 'pass': EETLIJST_PASS}

main_page = requests.post(login_url, data=values)
soup_main_page = BeautifulSoup(main_page.content, "lxml")

kosten_url = soup_main_page.find_all('a')[2]['href']
session_id = re.split('\W', kosten_url)[-1]

kosten_page = requests.get('http://eetlijst.nl/' + kosten_url)
soup_kosten_site = BeautifulSoup(kosten_page.content, "lxml")

today_status = soup_main_page.find_all('td', class_='r')

# Get the status of today
def get_status():
    eat, cook, away, unknown = [], [], [], []
    list_images = today_status[1].parent.find_all('img')
    for image in list_images:
        choice = image['src']
        person = re.split('\s', image['title'])[0]
        if choice == 'eet.gif':
            eat.append(person)
        elif choice == 'kook.gif':
            cook.append(person)
        elif choice == 'nop.gif':
            away.append(person)
        elif choice == 'leeg.gif':
            unknown.append(person)
    return eat, cook, away, unknown

# Get the ratio cook/eat
def get_ratio(person: int = None):
    list_ratio = []
    all_times_cook = soup_kosten_site.find('td', text='  Aantal keer gekookt').parent.find_all('td', class_="r")
    all_times_eat = soup_kosten_site.find('td', text='  Aantal keer meegegeten').parent.find_all('td', class_="r")
    for i in range(len(all_times_cook)):
        times_cook = int(all_times_cook[i].text)
        times_eat = int(all_times_eat[i].text)
        list_ratio.append(round(times_cook / times_eat, 3))
    return list_ratio if person == None else list_ratio[person]

def get_costs(person: int = None):
    list_costs = []
    all_costs = soup_kosten_site.find('td', text='  Kookt gemiddeld voor (p.p.)').parent.find_all('td', class_="r")[0:-1]
    for i in range(len(all_prices)):
        costs = float(all_prices[i].text.replace(',','.'))
        list_costs.append(round(costs, 2))
    return list_costs if person == None else list_costs[person]

def get_names(person: int = None):
    list_names = []
    all_names = soup_kosten_site.find('th', colspan='3').parent.find_all('th')[1:-1]
    for i in range(len(all_names)):
        list_names.append(all_names[i].text)
    return list_names if person == None else list_names[person]

def get_points(person: int = None):
    list_points = []
    all_points = soup_kosten_site.find_all('td', class_="l", colspan='3')[-1].parent.find_all('td', class_="r")[0:-1]
    for i in range(len(all_points)):
        list_points.append(all_points[i].text)
    return list_points if person == None else list_points[person]
