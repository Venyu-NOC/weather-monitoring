import sqlite3
from datetime import datetime
import logging


class SqliteDatabase:
    def __init__(self, station_id, logger=logging.getLogger('db.SQLite')):
        self.log = logger
        self.station_id = station_id

        self.__db_handle = sqlite3.connect('forecast.db')

        cursor = self.__db_handle.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.station_id}(name text, number integer primarykey, startTime text, endTime text, temperature real, windSpeed text, windDirection text, icon text, shortForecast text, detailedForecast text);''')
        cursor.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.__db_handle.close()
    
    def submit_forecast(self, forecast):
        rows = [
            (period["name"], period["number"], period["startTime"], period["endTime"], period["temperature"], period["windSpeed"], period["windDirection"], period["icon"], period["shortForecast"], period["detailedForecast"]) for period in forecast
        ]
        
        cursor = self.__db_handle.cursor()
        cursor.execute(f'''DELETE FROM {self.station_id.upper()};''')
        cursor.executemany(f'''INSERT INTO {self.station_id.upper()} 
                                        (name, number, startTime, endTime, temperature, windSpeed, windDirection, icon, shortForecast, detailedForecast) 
                                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
                                    rows)
        self.__db_handle.commit()
        cursor.close()

    def get_nday_forecast(self, ndays=7):
        query_string = f"""SELECT name, number, startTime, endTime, temperature, windSpeed, windDirection, icon, shortForecast, detailedForecast
                            FROM {self.station_id}
                            WHERE number >= 1
                            AND number <= ?
                            ORDER BY number ASC;"""
        
        self.__db_handle.row_factory = sqlite3.Row

        forecast = {
            "station_id": self.station_id
        }

        cursor = self.__db_handle.cursor()

        cursor.execute(query_string, (2 * ndays, ))
        forecast["periods"] = [dict(row) for row in cursor.fetchall()]
        cursor.close()

        return forecast
            