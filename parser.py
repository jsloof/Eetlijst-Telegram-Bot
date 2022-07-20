from bs4 import BeautifulSoup
from datetime import datetime
from os import getenv
from pytz import timezone
from requests import get, post
from typing import List, Optional, Tuple
from urllib.parse import parse_qs, urlparse


class Person:
    def __init__(self, index: int, name: str, user_id: Optional[int] = None):
        self._index: int = index
        self._name: str = name
        self._user_id: Optional[int] = user_id

    def __eq__(self, other):
        if isinstance(other, Person):
            return self._index == other._index and self._name == other._name and self._user_id == other._user_id
        return False

    def __str__(self):
        return self._name

    def __hash__(self):
        return hash(self._index)

    def get_index(self) -> int:
        return self._index

    def get_name(self) -> str:
        return self._name

    def get_user_id(self) -> Optional[int]:
        return self._user_id


class Parser:
    def __init__(self):
        username = getenv('EETLIJST_USER')
        if username is None:
            raise LookupError('Could not find EETLIJST_USER in config vars.')
        password = getenv('EETLIJST_PASS')
        if password is None:
            raise LookupError('Could not find EETLIJST_PASS in config vars.')

        response = post('https://eetlijst.nl/login.php', {'login': username, 'pass': password})
        if not response.ok:
            raise ConnectionError('Not possible to login.')

        session_id = parse_qs(urlparse(response.url).query).get('session_id')
        if session_id is None:
            raise ConnectionRefusedError('Incorrect username and/or password.')
        elif type(session_id) != list or len(session_id) < 1:
            raise LookupError('Could not find session ID.')
        else:
            self._session_id = session_id[0]

        self._main_page = BeautifulSoup(response.content, 'html.parser')
        self._cost_page = None
        self._statuses: list = []
        self._group: list = []

        row = self.get_main_page().find_all('a', class_='th')[:-2]
        for cell in row:
            index = len(self.get_group())
            name = cell.text
            user_id = int(getenv(name))
            self._group.append(Person(index, name, user_id))

    def get_main_page(self) -> BeautifulSoup:
        return self._main_page

    def get_cost_page(self) -> BeautifulSoup:
        if self._cost_page is None:
            response = get(f'https://eetlijst.nl/kosten.php?session_id={self._session_id}')
            self._cost_page = BeautifulSoup(response.content, 'html.parser')
        return self._cost_page

    def get_statuses(self) -> (List[Person], List[Person], List[Person]):
        """Returns the statuses of today."""
        eat, cook, unknown = [], [], []
        row = self.get_main_page().find_all('table')[3].find_all('tr')[1].find_all('td')[1:]
        for index, cell in enumerate(row):
            images = cell.find_all('img')
            for image in images:
                src = image['src']
                if 'eet.gif' == src:
                    eat.append(self.get_group()[index])
                elif 'kook.gif' == src:
                    cook.append(self.get_group()[index])
                elif 'leeg.gif' == src:
                    unknown.append(self.get_group()[index])
        return eat, cook, unknown

    def get_eaters(self) -> List[Person]:
        """Returns a list with the eaters."""
        return self.get_statuses()[0]

    def get_cook(self) -> List[Person]:
        """Returns a list with the cook(s)."""
        return self.get_statuses()[1]

    def get_unknown(self) -> List[Person]:
        """Returns a list with the persons with unknown status."""
        return self.get_statuses()[2]

    def get_cook_suggestion(self) -> Optional[Person]:
        """Returns the name of the person with the lowest cook/eat ratio."""
        potential_cooks = set(self.get_eaters() + self.get_unknown())
        for ratio, person in self.get_ratios():
            if person in potential_cooks:
                return person
        return None

    def get_ratios(self) -> List[Tuple[float, Person]]:
        """Returns a list with the ratio cook/eat per person."""
        list_ratio = []
        times_cook = self.get_cost_page().find('td', text='  Aantal keer gekookt').parent.find_all('td', class_='r')
        times_eat = self.get_cost_page().find('td', text='  Aantal keer meegegeten').parent.find_all('td', class_='r')
        for person in self.get_group():
            number_cook = int(times_cook[person.get_index()].text)
            number_eat = int(times_eat[person.get_index()].text)
            if number_eat == 0:
                list_ratio.append((0.0, person))
            else:
                list_ratio.append((number_cook / number_eat, person))
        return sorted(list_ratio, key=lambda x: x[0])

    def get_costs(self) -> List[Tuple[float, Person]]:
        """Returns a list with the average meal costs per person."""
        list_costs = []
        costs = self.get_cost_page().find('td', text='  Kookt gemiddeld voor (p.p.)').parent.find_all('td', class_='r')[:-1]
        for person in self.get_group():
            amount = float(costs[person.get_index()].text.strip().replace(',', '.'))
            list_costs.append((amount, person))
        return sorted(list_costs, key=lambda x: x[0])

    def get_points(self) -> List[Tuple[int, Person]]:
        """Returns a list with the cooking points per person."""
        list_points = []
        points = self.get_cost_page().find_all('td', class_='l', colspan='3')[-1].parent.find_all('td', class_='r')[:-1]
        for person in self.get_group():
            number = int(points[person.get_index()].text.strip())
            list_points.append((number, person))
        return sorted(list_points, key=lambda x: x[0])

    def get_balance(self) -> List[Tuple[float, Person]]:
        """Returns a list with the debit/credit per person."""
        list_owed_amount = []
        owed_amount = self.get_cost_page().find_all('tr', bgcolor='#DDDDDD')[0].find_all('td')[2:]
        for person in self.get_group():
            amount = float(owed_amount[person.get_index()].text.strip().replace(',', '.'))
            list_owed_amount.append((amount, person))
        return sorted(list_owed_amount, key=lambda x: x[0])

    def get_group(self) -> List[Person]:
        return self._group

    def set_status(self, person: Person, status: int):
        """Updates the status of the person at Eetlijst."""
        index = person.get_index()
        if status > 4:
            status = 4
        elif status < -4:
            status = -4
        now = datetime.now(timezone('Europe/Amsterdam'))
        today = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        data = {
            'session_id': self._session_id,
            'who': index,
            'what': status,
            'day[]': today,
            'submitwithform.x': 1
        }
        response = post('https://eetlijst.nl/main.php', data)
        if not response.ok:
            raise ConnectionError('Not possible to change status.')
