import logging
import os
import math
from nearby import RtlScanner, nearby
from scrape import flight_info
from flask import Flask
from flask_ask import Ask, request, session, question, statement

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
scanner = RtlScanner()

STATUSON = ['on','high','to on']
STATUSOFF = ['off','low', 'to off']

def round(x, unit = 100):
    return int(int(math.floor(x / float(unit))) * float(unit))

@ask.launch
def launch():
    speech_text = 'Welcome to Raspberry Pi Automation.'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('FlightIntent', mapping = {'status': 'status'})
def get_flights(status, room):
    ##Parse aircraft.json
    flight, dist = nearby(scanner)
    info = flight_info(flight)
    typ = info['aircraft'] if info is not None else None
    if typ:
        if typ[0].upper() in 'AEIOU': article = 'an'
        else: article = 'a'
        typ_str = 'is {} {} with'.format(article, typ)
    else:
        typ_str = 'has'
    alt = round(flight['altitude'])
    dist = int(dist)
    if dist == 1: dist = '{} mile'.format(dist)
    else: dist = '{} miles'.format(dist)

    if flight is None:
        return statement("Could not find any planes nearby. Try again later.")
    else:
        return statement('<speak>The closest plane {} callsign <say-as interpret-as="spell-out">{}</say-as> . It\'s {} away, with an altitude of {} feet.</speak>'.format(typ_str, flight['callsign'].replace(' ', ''), \
            dist, alt))

#<say-as interpret-as="spell-out">hello</say-as>

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('AMAZON.FallbackIntent')
def help():
    return statement("I didn't understand you. Ask the raspberry pi what planes are overhead.")

@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
