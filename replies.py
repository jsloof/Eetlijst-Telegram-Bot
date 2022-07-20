from parser import Parser, Person
from telegram.utils.helpers import mention_html
from typing import List, Tuple


def eetlijst() -> Tuple[str, List[Person]]:
    """Replies a dict with the status per person and the unknown persons."""
    p = Parser()
    eat, cook, unknown = p.get_statuses()
    present = eat + cook
    number = len(present)
    num_eat = len(eat)
    num_cook = len(cook)
    num_unknown = len(unknown)
    for person in p.get_group():
        guests = present.count(person) - 1
        if guests > 0:
            if person in cook:
                if guests == 1:
                    eat[eat.index(person)] = f'1 mee-eter van {person}'
                elif guests == 2:
                    eat[eat.index(person)] = f'2 mee-eters van {person}'
                else:
                    eat[eat.index(person)] = f'3 (of meer) mee-eters van {person}'
                    number = f'{number} (of meer)'
            else:
                if guests == 1:
                    eat[eat.index(person)] = f'{person} +1 mee-eter'
                elif guests == 2:
                    eat[eat.index(person)] = f'{person} +2 mee-eters'
                else:
                    eat[eat.index(person)] = f'{person} +3 (of meer) mee-eters'
                    number = f'{number} (of meer)'
            eat = list(filter(person.__ne__, eat))
    reply = ''
    if num_cook > 0:
        reply += f'{list_to_str(cook)}'
        reply += ' gaat' if num_cook == 1 else ' gaan'
        reply += ' koken voor'
        reply += ' tot nu toe' if num_unknown > 0 else ''
        reply += ' alleen zichzelf.\n' if number == 1 else f' {number} personen.\n'
    if num_eat > 0:
        reply += f'{list_to_str(eat)}'
        reply += ' eet' if num_eat == 1 else ' eten'
        reply += ' mee.\n'
    if num_unknown > 0:
        reply += f'{list_to_str(unknown)}'
        reply += ' moet' if num_unknown == 1 else ' moeten'
        reply += ' zich nog inschrijven.\n'
    if reply == '':
        reply = 'Niemand eet mee.'
    return reply, p.get_unknown()


def kok() -> str:
    """Replies the (suggested) cook."""
    p = Parser()
    cook = p.get_cook()
    num_cook = len(cook)
    if num_cook == 0:
        if len(p.get_eaters() + p.get_unknown()) == 0:
            reply = 'Niemand eet mee.'
        else:
            person = p.get_cook_suggestion()
            if person.get_user_id():
                person = mention_html(person.get_user_id(), person.get_name())
            reply = f'Er gaat nog niemand koken.\n{person} staat het laagst qua verhouding.'
    else:
        reply = f'{list_to_str(cook)}'
        reply += ' gaat' if num_cook == 1 else ' gaan'
        reply += ' koken.'
    return reply


def balans() -> str:
    """Replies the debit/credit per person."""
    p = Parser()
    reply = '<b>Balans:</b>\n'
    for amount, person in p.get_balance():
        if amount < 0:
            reply += f'<code>-€{"%.2f" % -amount}</code> ({person})\n'
        else:
            reply += f'<code> €{"%.2f" % amount}</code> ({person})\n'
    return reply


def kookkosten() -> str:
    """Replies the average meal costs per person."""
    p = Parser()
    reply = '<b>Gemiddelde kookkosten:</b>\n'
    for costs, person in p.get_costs():
        reply += f'<code>€{"%.2f" % costs}</code> ({person})\n'
    return reply


def kookpunten() -> str:
    """Replies the cooking points per person."""
    p = Parser()
    reply = '<b>Kookpunten:</b>\n'
    for points, person in p.get_points():
        reply += '<code>' if points < 0 else '<code> '
        reply += f'{points}</code> ({person})\n'
    return reply


def verhouding() -> str:
    """Replies the ratio cook/eat per person."""
    p = Parser()
    reply = '<b>Verhouding koken/eten:</b>\n'
    for ratio, person in p.get_ratios():
        reply += f'<code>{"%.3f" % ratio}</code> ({person})\n'
    return reply


def set_eetlijst(user_id: int, status: int) -> str:
    """Replies the status update of the person."""
    p = Parser()
    if status > 0 and len(p.get_cook()) > 0:
        return 'Sorry, er gaat al iemand koken.'
    else:
        person = next((person for person in p.get_group() if person.get_user_id() == user_id), None)
        if person is None:
            return 'Sorry, je hebt hier geen toestemming voor.'
        try:
            if status < 0:
                reply = f'Oke, ik zet {person} op mee-eten'
            elif status > 0:
                reply = f'Oke, ik zet {person} op koken'
            else:
                p.set_status(person, 0)
                return f'Oke, ik schrijf {person} uit.'
            total = abs(status)
            if total == 2:
                reply += ' met 1 gast'
            elif total == 3:
                reply += ' met 2 gasten'
            elif total > 3:
                reply += ' met 3 (of meer) gasten'
            p.set_status(person, status)
        except ConnectionError:
            return 'Sorry, het is niet gelukt om je status aan te passen.'
    return reply


def list_to_str(names: list) -> str:
    return ', '.join([str(name) for name in names[:-2]] + [' en '.join([str(name) for name in names[-2:]])])
