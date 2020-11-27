from bs4 import BeautifulSoup
import os, re, requests

class Parser:

    def __init__(self):
        self.EETLIJST_USER = os.environ['EETLIJST_USER']
        self.EETLIJST_PASS = os.environ['EETLIJST_PASS']

        self.login_url = 'http://eetlijst.nl/login.php'
        self.values = {'login': self.EETLIJST_USER, 'pass': self.EETLIJST_PASS}

        self.main_page = requests.post(self.login_url, data=self.values)
        self.soup_main_page = BeautifulSoup(self.main_page.content, "html.parser")

        self.kosten_url = self.soup_main_page.find_all('a')[2]['href']
        self.session_id = re.split('\W', self.kosten_url)[-1]

        self.kosten_page = requests.get('http://eetlijst.nl/' + self.kosten_url)
        self.soup_kosten_site = BeautifulSoup(self.kosten_page.content, "html.parser")

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
            list_costs.append(all_costs[i].text.strip())
        return list_costs if person == None else list_costs[person]

    # Get the names
    def get_names(self, person: int = None):
        list_names = []
        all_names = self.soup_kosten_site.find('th', colspan='3').parent.find_all('th')[1:-1]
        for i in range(len(all_names)):
            list_names.append(all_names[i].text.strip())
        return list_names if person == None else list_names[person]

    #Get the cooking points
    def get_points(self, person: int = None):
        list_points = []
        all_points = self.soup_kosten_site.find_all('td', class_="l", colspan='3')[-1].parent.find_all('td', class_="r")[0:-1]
        for i in range(len(all_points)):
            list_points.append(all_points[i].text.strip())
        return list_points if person == None else list_points[person]
