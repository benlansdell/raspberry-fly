# RaspberryFly

Flask-ask code for an alexa skill that tells you about planes flying overhead. Meaning you can ask your Alexa things like:

`Alexa ask raspberry pi what planes are overhead`

and it will read the information from your local ADSB receiver. This does mean you must have one setup locally for this to work. If you're not interested in alexa using your own data, there are published Alexa skills out there that will probe ADSBExchange for nearby flights. Of course, ADSBExchange may not have good coverage in your area. 

This repo is a combination of these two blog posts/repos:

* https://www.hackster.io/nishit-patel/controlling-raspberry-pi-using-alexa-33715b.
* https://github.com/Syps/alexa-airplane-spotter

The skill for Alexa uses flask-ask. For establishing connection to the raspberry pi it uses ngrok. ngrok establishes a HTTP tunnel from Raspberry Pi to Alexa. The endpoint url will change every time ngrok is restarted, as an alternative you can use pagekite.

See the accompanying blog post for more information on how to get everything setup. 
