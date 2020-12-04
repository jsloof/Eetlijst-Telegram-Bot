from parser import Parser

def eetlijst():
    """Replies a dict with the status per person and the unknown persons."""
    ps = Parser()
    eaters, cook, absent, unknown = ps.eetlijst
    reply = ''
    unknown_persons = []
    if len(cook) > 0:
        number = len(eaters + cook)
        reply += ' en'.join(str(cook).replace('[','').replace('\'','').replace(']','').rsplit(',', 1))
        reply += ' gaat' if len(cook) == 1 else ' gaan'
        reply += ' koken voor'
        reply += ' tot nu toe' if len(unknown) > 0 else ''
        reply += ' alleen zichzelf.\n' if number == 1 else f' {number} personen.\n'
    if len(eaters) > 0:
        reply += ' en'.join(str(eaters).replace('[','').replace('\'','').replace(']','').rsplit(',', 1))
        reply += ' eet' if len(eaters) == 1 else ' eten'
        reply += ' mee.\n'
    if len(unknown) > 0:
        reply += ' en'.join(str(unknown).replace('[','').replace('\'','').replace(']','').rsplit(',', 1))
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
        reply = ' en'.join(str(cook).replace('[','').replace('\'','').replace(']','').rsplit(',', 1))
        reply += ' gaat' if len(cook) == 1 else ' gaan'
        reply += ' koken.'
    return reply

def kookpunten():
    """Replies the cooking points per person."""
    ps = Parser()
    points = ps.get_points()
    reply = '<b>Kookpunten:</b>\n'
    for index, name in enumerate(ps.names):
        reply += f'<code>{points[index]}</code> ({name})\n'
    return reply

def kosten():
    """Replies the average meal costs per person."""
    ps = Parser()
    costs = ps.get_costs()
    reply = '<b>Gemiddelde kosten:</b>\n'
    for index, name in enumerate(ps.names):
        reply += f'<code>€{costs[index]}</code> ({name})\n'
    return reply

def verhouding():
    """Replies the ratio cook/eat per person."""
    ps = Parser()
    ratio = ps.get_ratio()
    reply = '<b>Verhouding koken/eten:</b>\n'
    for index, name in enumerate(ps.names):
        reply += f'<code>{ratio[index]}</code> ({name})\n'
    return reply

def set_eetlijst(user_id, status):
    """Replies the status update of the person."""
    ps = Parser()
    if status == 1 and len(ps.get_cook()) > 0:
        reply = 'Sorry, er gaat al iemand koken.'
    else:
        try:
            user_ids = list(ps.persons.values())
            person_index = user_ids.index(str(user_id))
            name = ps.names[person_index]
            ps.set_eetlijst(person_index, status)
            if status == 0:
                reply = f'Oke, ik schrijf {name} uit.'
            elif status == -1:
                reply = f'Oke, ik zet {name} op mee-eten.'
            elif status == 1:
                reply = f'Oke, ik zet {name} op koken.'
        except:
            reply = 'Sorry, het is niet gelukt om je status aan te passen.'
    return reply
