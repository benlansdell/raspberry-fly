from logger import logger
import settings
import requests
import json
import math

TAKE_DUMP = True
EARTH_RADIUS = 6371e3

def distance_in_miles(lat1, lon1, lat2, lon2):
    phi1 = lat1*math.pi/180           # phi, lambda in radians
    phi2 = lat2*math.pi/180
    del_phi = (lat2 - lat1)*math.pi/180
    del_lambda = (lon2 - lon1)*math.pi/180
    a = math.sin(del_phi/2)*math.sin(del_phi/2) + \
      math.cos(phi1)*math.cos(phi2)*math.sin(del_lambda/2)*math.sin(del_lambda/2)

    c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = EARTH_RADIUS*c;            # in meters
    return d/1600                  # convert to miles

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

class Scanner:
    '''
    Returns a list of opensky_api StateVector's
    containing data on nearby planes
    '''
    def nearby():
        raise NotImplementedError

    def distance_from_window(self, flight):
        window_lat, window_lng = settings.coords['window']
        return distance_in_miles(window_lat, window_lng, flight['latitude'], flight['longitude'])

    def closest(self):
        flights = self.nearby()
        return min(flights, key=self.distance_from_window) if flights else None

class RtlScanner(Scanner):
    ENDPOINT = settings.data_endpoint
    class RtlException(Exception):
        def __init__(self):
            message = """
                Failed to establish connection to dump1090 json endpoint.
                Check that ./dump1090 --net is running, or that SSH tunnel
                is set up if dump1090 running on another computer.
                """
            super(RtlScanner.RtlException, self).__init__(message)

    def __init__(self, assert_conn=True):
        if assert_conn:
            try:
                data = requests.get(self.ENDPOINT)
            except requests.exceptions.ConnectionError:
                raise RtlScanner.RtlException()

    def _as_state_vector(self, data_pt):
        vector = {}
        vector['icao24'] = data_pt['hex'] # icao24
        vector['callsign'] = data_pt['flight'] # callsign
        vector['longitude'] = data_pt['lon'] # longitude
        vector['latitude'] = data_pt['lat'] # latitude
        alt = 0
        for alt_key in ['altitude', 'alt_geom', 'alt_baro']:
            if alt_key in data_pt:
                alt = data_pt[alt_key]
                break
        vector['altitude'] = alt #altitude 
        if vector['altitude'] == 'ground': vector['altitude'] = 0
        vector['on_ground'] = False # on ground
        return vector

    def _valid_data(self, data_pt):
        reqs_keys = ['hex', 'flight', 'lon', 'lat']
        for k in reqs_keys:
            if k not in data_pt:
                return False
        if data_pt.get('seen', 1000) > 35: # 'seen' == seconds since last msg
            return False # stale messages == out of sight (ideally)
        if len(data_pt.get('hex', '').strip()) == 0:
            return False # invalid hex code
        return True

    def nearby(self):
        res = requests.get(self.ENDPOINT) # localhost:8080/data.json
        data = json.loads(res.text)['aircraft']
        data = filter(self._valid_data, data)
        logger.info(data)
        return [self._as_state_vector(v) for v in data]

def get_scanner():
    return RtlScanner()

def nearby(scanner):
    logger.info('scanning')
    flight = scanner.closest()
    dist = scanner.distance_from_window(flight)
    logger.info('chose flight {}'.format(flight))
    return (flight, dist) if flight else (None, None)

if __name__ == '__main__':
    scanner = get_scanner()
    nearby(scanner)
