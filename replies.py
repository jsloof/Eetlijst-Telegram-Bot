from parser import Parser

def eetlijst():
    ps = Parser()
    eaters, cook, absent, unknown = ps.get_eetlijst()
    if len(cook) == 0:
        reply = "Er gaat nog niemand koken.\n"
    else:
        reply = str(cook).replace('[','').replace('\'','').replace(']','')
        reply += " gaat" if len(cook) == 1 else " gaan"
        reply += " koken.\n"
    if len(eaters) > 0:
        reply += str(eaters).replace('[','').replace('\'','').replace(']','')
        reply += " eet" if len(eaters) == 1 else " eten"
        reply += " mee.\n"
    if len(unknown) > 0:
        reply += str(unknown).replace('[','').replace('\'','').replace(']','')
        reply += " moet" if len(unknown) == 1 else " moeten"
        reply += " zich nog inschrijven.\n"
    return reply

def kok():
    ps = Parser()
    cook = ps.get_cook()
    if len(cook) == 0:
        zipped = str(dict(zip(ps.get_ratio(), ps.get_names())))
        reply = "Er gaat nog niemand koken, maar dit is de verhouding koken/eten:\n"
        reply += zipped.replace('{','<code>').replace(': \'','</code> (').replace('\', ',')\n<code>').replace('\'}',')')
    else:
        reply = str(cook).replace('[','').replace('\'','').replace(']','')
        reply += " gaat" if len(cook) == 1 else " gaan"
        reply += " koken."
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
    reply = zipped.replace('{','<b>Verhouding koken/eten:</b>\n<code>').replace(': \'','</code> (').replace('\', ',')\n<code>').replace('\'}',')')
    return reply
