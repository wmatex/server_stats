#!/usr/bin/python2
# Logs computer temperature and fan speed to database
# Intended to run via cron
from subprocess import check_output
import re
import _mysql
import db

class Logger:
    def __init__(self):
        self._sensors = { 
                'Processor': (1, r'temp1:\s+\+([0-9]+\.[0-9])'),
                'Case': (2, r'M/B Temp:\s+\+([0-9]+\.[0-9])'),
                'Fan': (3, r'fan1:\s+([0-9]+)')
                }
        self._sensors_bin = "sensors"


    def log(self):
        output = check_output([self._sensors_bin]).decode("utf-8")
        
        try:
            con = _mysql.connect(db.server, db.name, db.password, db.dbname)

            for (name, sensor) in self._sensors.items():
                m = re.search(sensor[1], output, re.M)
                if m != None:
                    con.query("INSERT INTO sensor_log(sensor, value) VALUES("+str(sensor[0])+", "+str(m.group(1))+");")

        except _mysql.Error, e:
            print("MySQL error: " % (e.args[1]))

        finally:
            if con:
                con.close()



# Main block
if __name__ == "__main__":
    log = Logger()
    log.log()
