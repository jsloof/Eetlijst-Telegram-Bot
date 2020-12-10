from parser import Parser

def eetlijst():
    """Replies a dict with the status per person and the unknown persons."""
    ps = Parser()
    eaters, cook, absent, unknown = ps.eetlijst
    present = eaters + cook
    number = len(present)
    for person in ps.names:
        guests = present.count(person) - 1
        if guests > 0:
            if person in cook:
                if guests == 1:
                    eaters[eaters.index(person)] = f'1 mee-eter van {person}'
                elif guests == 2:
                    eaters[eaters.index(person)] = f'2 mee-eters van {person}'
                else:
                    eaters[eaters.index(person)] = f'3 (of meer) mee-eters van {person}'
                    number = f'{number} (of meer)'
            else:
                if guests == 1:
                    eaters[eaters.index(person)] = f'{person} +1 mee-eter'
                elif guests == 2:
                    eaters[eaters.index(person)] = f'{person} +2 mee-eters'
                else:
                    eaters[eaters.index(person)] = f'{person} +3 (of meer) mee-eters'
                    number = f'{number} (of meer)'
            eaters = list(filter((person).__ne__, eaters))
    reply = ''
    unknown_persons = []
    if len(cook) > 0:
        reply += f'{names_to_str(cook)}'
        reply += ' gaat' if len(cook) == 1 else ' gaan'
        reply += ' koken voor'
        reply += ' tot nu toe' if len(unknown) > 0 else ''
        reply += ' alleen zichzelf.\n' if number == 1 else f' {number} personen.\n'
    if len(eaters) > 0:
        reply += f'{names_to_str(eaters)}'
        reply += ' eet' if len(eaters) == 1 else ' eten'
        reply += ' mee.\n'
    if len(unknown) > 0:
        reply += f'{names_to_str(unknown)}'
        reply += ' moet' if len(unknown) == 1 else ' moeten'
        reply += ' zich nog inschrijven.\n'
        for name in unknown:
            unknown_persons.append({'name': name, 'telegram_id': ps.persons[name]})
    if reply == '':
        reply = 'Niemand eet mee.'
    return {'reply': reply, 'unknown_persons': unknown_persons}

def kok():
    """Replies the (suggested) cook."""
    ps = Parser()
    cook = ps.get_cook()
    if len(cook) == 0:
        if len(ps.get_eaters() + ps.get_unknown()) == 0:
            reply = 'Niemand eet mee.'
        else:
            reply = f'Er gaat nog niemand koken.\n{ps.get_cook_suggestion()} staat het laagst qua verhouding.'
    else:
        reply = f'{names_to_str(cook)}'
        reply += ' gaat' if len(cook) == 1 else ' gaan'
        reply += ' koken.'
    return reply

def balans():
    """Replies the owed amount per person."""
    reply = '<b>Balans:</b>\n'
    for amount, name in Parser().get_owed_amount():
        if amount < 0:
            reply += f'<code>-€{"%.2f" % -amount}</code> ({name})\n'
        else:
            reply += f'<code> €{"%.2f" % amount}</code> ({name})\n'
    return reply

def kookkosten():
    """Replies the average meal costs per person."""
    reply = '<b>Gemiddelde kookkosten:</b>\n'
    for costs, name in Parser().get_costs():
        reply += f'<code>€{"%.2f" % costs}</code> ({name})\n'
    return reply

def kookpunten():
    """Replies the cooking points per person."""
    reply = '<b>Kookpunten:</b>\n'
    for points, name in Parser().get_points():
        reply += '<code>' if points < 0 else '<code> '
        reply += f'{points}</code> ({name})\n'
    return reply

def verhouding():
    """Replies the ratio cook/eat per person."""
    reply = '<b>Verhouding koken/eten:</b>\n'
    for ratio, name in Parser().get_ratios():
        reply += f'<code>{"%.3f" % ratio}</code> ({name})\n'
    return reply

def names_to_str(list):
    return ' en'.join(str(list).replace('[','').replace('\'','').replace(']','').rsplit(',', 1))

def set_eetlijst(user_id, status):
    """Replies the status update of the person."""
    ps = Parser()
    if status > 0 and len(ps.get_cook()) > 0:
        return 'Sorry, er gaat al iemand koken.'
    else:
        try:
            user_ids = list(ps.persons.values())
            person_index = user_ids.index(str(user_id))
            name = ps.names[person_index]
            if status < 0:
                reply = f'Oke, ik zet {name} op mee-eten'
            elif status > 0:
                reply = f'Oke, ik zet {name} op koken'
            else:
                ps.set_eetlijst(person_index, 0)
                return f'Oke, ik schrijf {name} uit.'
            total = abs(status)
            if total == 2:
                reply += ' met 1 gast'
            elif total == 3:
                reply += ' met 2 gasten'
            elif total > 3:
                reply += ' met 3 (of meer) gasten'
                if status < 0:
                    status = -4
                else:
                    status = 4
            ps.set_eetlijst(person_index, status)
        except:
            return 'Sorry, het is niet gelukt om je status aan te passen.'
    return reply + '.'
