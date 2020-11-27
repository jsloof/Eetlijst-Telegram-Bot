from parser import Parser

def eetlijst():
    ps = Parser()
    reply = ""
    if ps.get_eetlijst()[1] != []:
        reply += str(ps.get_eetlijst()[1]).replace('[','').replace('\'','').replace(']','') + " gaat koken.\n"
    if ps.get_eetlijst()[0] != []:
        reply += str(ps.get_eetlijst()[0]) + " eten mee.\n"
    if ps.get_eetlijst()[3] != []:
        reply += str(ps.get_eetlijst()[3]) + " moeten zich nog inschrijven."
    return reply

def kok():
    ps = Parser()
    if ps.get_eetlijst()[1] != []:
        reply = str(ps.get_eetlijst()[1]) + " gaat koken."
    else:
        reply = "Wie wil er koken?"
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
