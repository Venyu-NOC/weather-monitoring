from datetime import datetime, timedelta
import logging

import requests

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from db.influx import InfluxDatabase


log = logging.getLogger('weather.backend.scheduler')

now = datetime.now()
next_12 = now - timedelta(minutes=now.minute) - timedelta(hours=now.hour+6)
next_hour = now + timedelta(minutes=60 - now.minute)

every_15_minutes = IntervalTrigger(minutes=15)
every_12_hours = IntervalTrigger(hours=12, start_date=next_12)
every_hour = IntervalTrigger(hours=1, start_date=next_hour)

scheduler = BackgroundScheduler()


def schedule_jobs(weather_data):
    for station in weather_data["locations"]:
        station_id = station["id"]
        log.info(f'scheduling update tasks for {station_id}')

        log.info('first-time conditions update')
        update_conditions(station)

        log.info('scheduling conditions update')
        scheduler.add_job(update_conditions, every_15_minutes, args=[station, ])

    scheduler.start()


def update_conditions(station):
    log.debug('connection to current conditions database')
    with InfluxDatabase(host='influx') as database:
        log.debug('downloading conditions data')
        r = requests.get(station["urls"]["conditions"])

        if r.status_code == 200:
            log.debug('adding to database')
            database.submit_conditions(station["id"], r.json())
        else:
            log.error(f'encountered an error downloading condition data for {station["id"]}: {r.status_code}')

