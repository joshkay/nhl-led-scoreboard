import ephem
#import logging
import debug


class Dimmer(object):
    def __init__(self, scheduler, sleepEvent):
        self._observer = ephem.Observer()
        self._observer.pressure = 0
        self._observer.horizon = '-6'
        # You can get your IP by running: curl https://ipinfo.io/loc or use https://latlon.net (this will get you more specific coordinates)
        self._observer.lat = '49.88147'
        self._observer.lon = '-97.30459'

        self.brightness = 100
        self.sleepEvent = sleepEvent

        self.update()

        # Run every 5 minutes
        scheduler.add_job(self.update, 'cron', minute='*/5')

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
