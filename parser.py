from bs4 import BeautifulSoup
from selenium import webdriver
import os, re, requests

class Parser:

    def __init__(self):
        """Initiates the Parser object."""
        eetlijst_user = os.environ['EETLIJST_USER']
        eetlijst_pass = os.environ['EETLIJST_PASS']

        login_url = 'http://eetlijst.nl/login.php'
        login_data = {'login': eetlijst_user, 'pass': eetlijst_pass}
        main_page = requests.post(login_url, data=login_data)
        self.soup_main_page = BeautifulSoup(main_page.content, 'html.parser')

        kosten_url = self.soup_main_page.find_all('a')[2]['href']
        kosten_page = requests.get('http://eetlijst.nl/' + kosten_url)
        self.soup_kosten_page = BeautifulSoup(kosten_page.content, 'html.parser')
        self.session_id = re.split('\W', kosten_url)[-1]

        self.persons = self.get_persons()
        self.names = list(self.persons.keys())
        self.eetlijst = self.get_eetlijst()

    def get_eetlijst(self):
        """Returns the eetlijst of today."""
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
                person = self.names[len(set(eaters + cook + absent + unknown))]
                unknown.append(person)
        return eaters, cook, absent, unknown

    def get_eaters(self):
        """Returns a list with the eaters."""
        return self.eetlijst[0]

    def get_cook(self):
        """Returns a list with the cook(s)."""
        return self.eetlijst[1]

    def get_absent(self):
        """Returns a list with the absent persons."""
        return self.eetlijst[2]

    def get_unknown(self):
        """Returns a list with the persons with unknown status."""
        return self.eetlijst[3]

    def get_cook_suggestion(self):
        """Returns the name of the person with the lowest cook/eat ratio."""
        ratio = self.get_ratio()
        ratio_sorted = sorted(ratio)
        potential_cooks = list(set(self.get_eaters() + self.get_unknown()))
        name = ''
        for r in ratio_sorted:
            index = ratio.index(r)
            name = self.names[index]
            if name in potential_cooks:
                break
        return name

    def get_ratio(self):
        """Returns a list with the ratio cook/eat per person."""
        list_ratio = []
        all_times_cook = self.soup_kosten_page.find('td', text='  Aantal keer gekookt').parent.find_all('td', class_='r')
        all_times_eat = self.soup_kosten_page.find('td', text='  Aantal keer meegegeten').parent.find_all('td', class_='r')
        for i in range(len(all_times_cook)):
            times_cook = int(all_times_cook[i].text)
            times_eat = int(all_times_eat[i].text)
            if times_eat == 0:
                list_ratio.append(0.000)
            else:
                list_ratio.append(round(times_cook / times_eat, 3))
        return list_ratio

    def get_costs(self):
        """Returns a list with the average meal costs per person."""
        list_costs = []
        all_costs = self.soup_kosten_page.find('td', text='  Kookt gemiddeld voor (p.p.)').parent.find_all('td', class_='r')[0:-1]
        for i in range(len(all_costs)):
            list_costs.append(all_costs[i].text.strip())
        return list_costs

    def get_points(self):
        """Returns a list with the cooking points per person."""
        list_points = []
        all_points = self.soup_kosten_page.find_all('td', class_='l', colspan='3')[-1].parent.find_all('td', class_='r')[0:-1]
        for i in range(len(all_points)):
            list_points.append(all_points[i].text.strip())
        return list_points

    def get_persons(self):
        """Returns a dict with the names and telegram_ids of the persons."""
        persons = {}
        all_names = self.soup_kosten_page.find('th', colspan='3').parent.find_all('th')[1:-1]
        for name in all_names:
            stripped_name = name.text.strip()
            try:
                telegram_id = os.environ[stripped_name]
            except:
                telegram_id = ''
            persons[stripped_name] = telegram_id
        return persons

    def set_eetlijst(self, person_index, status):
        """Updates the status of the person at Eetlijst."""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.binary_location = '/app/.apt/usr/bin/google-chrome'
        driver = webdriver.Chrome(executable_path='/app/.chromedriver/bin/chromedriver', chrome_options=chrome_options)
        driver.get(f'http://www.eetlijst.nl/main.php?session_id={self.session_id}&who={person_index}&what={status}')
        elem = driver.find_element_by_name('submitwithform')
        elem.click()
        driver.quit()
