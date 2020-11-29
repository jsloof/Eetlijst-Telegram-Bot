from bs4 import BeautifulSoup
import os, re, requests

class Parser:

    def __init__(self):
        eetlijst_user = os.environ['EETLIJST_USER']
        eetlijst_pass = os.environ['EETLIJST_PASS']

        login_url = 'http://eetlijst.nl/login.php'
        login_data = {'login': eetlijst_user, 'pass': eetlijst_pass}
        main_page = requests.post(login_url, data=login_data)
        self.soup_main_page = BeautifulSoup(main_page.content, "html.parser")

        kosten_url = self.soup_main_page.find_all('a')[2]['href']
        kosten_page = requests.get('http://eetlijst.nl/' + kosten_url)
        self.soup_kosten_page = BeautifulSoup(kosten_page.content, "html.parser")

        self.eetlijst = self.get_eetlijst()
        self.persons = self.get_persons()

    # Returns the eetlijst of today
    def get_eetlijst(self):
        eaters, cook, absent, unknown = [], [], [], []
        list_images = self.soup_main_page.find_all('td', class_='r')[1].parent.find_all('img')
        for image in list_images:
            choice = image['src']
            person = re.split('\s', image['title'])[0]
            if choice == 'eet.gif':
                eaters.append(person)
            elif choice == 'kook.gif':
                cook.append(person)
            elif choice == 'nop.gif':
                absent.append(person)
            else:
                person = list(self.persons.keys())[len(set(eaters + cook + absent + unknown))]
                unknown.append(person)
        return eaters, cook, absent, unknown

    # Returns a list with the eaters
    def get_eaters(self):
        return self.eetlijst[0]

    # Returns a list with the cook(s)
    def get_cook(self):
        return self.eetlijst[1]

    # Returns a list with the absent persons
    def get_absent(self):
        return self.eetlijst[2]

    # Returns a list with the persons with unknown status
    def get_unknown(self):
        return self.eetlijst[3]

    # Returns a list with the ratio cook/eat per person
    def get_ratio(self):
        list_ratio = []
        all_times_cook = self.soup_kosten_page.find('td', text='  Aantal keer gekookt').parent.find_all('td', class_="r")
        all_times_eat = self.soup_kosten_page.find('td', text='  Aantal keer meegegeten').parent.find_all('td', class_="r")
        for i in range(len(all_times_cook)):
            times_cook = int(all_times_cook[i].text)
            times_eat = int(all_times_eat[i].text)
            list_ratio.append(round(times_cook / times_eat, 3))
        return list_ratio

    # Returns a list with the average meal costs per person
    def get_costs(self):
        list_costs = []
        all_costs = self.soup_kosten_page.find('td', text='  Kookt gemiddeld voor (p.p.)').parent.find_all('td', class_="r")[0:-1]
        for i in range(len(all_costs)):
            list_costs.append(all_costs[i].text.strip())
        return list_costs

    # Returns a list with the cooking points per person
    def get_points(self):
        list_points = []
        all_points = self.soup_kosten_page.find_all('td', class_="l", colspan='3')[-1].parent.find_all('td', class_="r")[0:-1]
        for i in range(len(all_points)):
            list_points.append(all_points[i].text.strip())
        return list_points

    # Returns a dict with the names and telegram_ids of the persons
    def get_persons(self, person: str = None):
        persons = {}
        all_names = self.soup_kosten_page.find('th', colspan='3').parent.find_all('th')[1:-1]
        for name in all_names:
            stripped_name = name.text.strip()
            persons[stripped_name] = os.environ[stripped_name]
        return persons if person == None else (person, persons[person])
