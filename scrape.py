from pymongo import MongoClient
from logger import logger

def db_results(icao24):
    client = MongoClient('localhost:27017')
    db = client.AircraftData
    result = db.Registration.find_one({
        'icao': icao24.upper()
    })

    if not result:
        return None

    airline = result['operator'].encode('ascii')
    reg_no = result['regid'].encode('ascii')
    aircraft = result['type'].encode('ascii')

    return reg_no, aircraft, airline

def flight_info(flight):
    results = db_results(flight['icao24'])

    if not results:
        logger.info('could find flight in db (flight={})'.format(flight))
        return None

    reg_no, aircraft, airline = results
    aircraft = ''.join(aircraft.split('-')[:-1])

    data = {
            'aircraft': aircraft,
            'airline': airline
    }

    if not reg_no:
        logger.info('couldn\'t find aircraft icao ({}) in db'.format(flight['icao24']))

    return data
