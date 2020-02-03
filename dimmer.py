import ephem
#import logging
import debug
import geocoder


class Dimmer(object):
    def __init__(self, scheduler, sleepEvent):
        self._observer = ephem.Observer()
        self._observer.pressure = 0
        self._observer.horizon = '-6'

        g = geocoder.ip('me')
        debug.info("Location is: " + str(g.latlng))
        self._observer.lat = g.lat
        self._observer.lon = g.lng

        self.brightness = 1
        self.sleepEvent = sleepEvent

        self.update()

        # Run every 10 minutes
        scheduler.add_job(self.update, 'cron', minute='*/10')

    def update(self):
        self._observer.date = ephem.now()
        #lt = ephem.localtime(self._observer.date)
        #debug.info(lt)
        morning = self._observer.next_rising(ephem.Sun(), use_center=True)
        night = self._observer.next_setting(ephem.Sun(), use_center=True)
        #sunrise = ephem.localtime(morning)
        #sunset = ephem.localtime(night)
        #debug.info(sunrise)
        #debug.info(sunset)

        # Very simplistic way of handling the day/night but it works
        if morning < night:
            # Morning is sooner, so it must be night
            debug.info("It is night time")
            self.brightness = 5
            self.sleepEvent.set()
            self.sleepEvent.clear()
        else:
            debug.info("It is day time")
            self.brightness = 55
            self.sleepEvent.set()
            self.sleepEvent.clear()
