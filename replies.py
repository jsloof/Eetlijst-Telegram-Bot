import parser as ps

def eetlijst():
    reply = ""
    if get_status()[1] != []:
        reply += str(ps.get_status()[1]) + " gaat koken.\n"
    if get_status()[0] != []:
        reply += str(ps.get_status()[1]) + " eten mee.\n"
    if get_status()[3] != []:
        reply += str(ps.get_status()[1]) + " moeten zich nog inschrijven."
    return reply

def kok():
    if get_status()[1] != []:
        reply = str(ps.get_status()[1]) + " gaat koken."
    else:
        reply = "Wie wil er koken?"
    return reply

def kookpunten():
    zipped = str(dict(zip(ps.get_points(), ps.get_names())))
    reply = zipped.replace('{\'','<b>Kookpunten:</b>\n<code>').replace('\': \'','</code> (').replace('\', \'',')\n<code>').replace('\'}',')')
    return reply

def kosten():
    zipped = str(dict(zip(ps.get_costs(), ps.get_names())))
    reply = zipped.replace('{\'','<b>Gemiddelde kosten:</b>\n<code>€').replace('\': \'','</code> (').replace('\', \'',')\n<code>€').replace('\'}',')')
    return reply

def verhouding():
    zipped = str(dict(zip(ps.get_ratio(), ps.get_names())))
    reply = zipped.replace('{\'','<b>Verhouding koken/eten:</b>\n<code>').replace('\': \'','</code> (').replace('\', \'',')\n<code>').replace('\'}',')')
    return reply
