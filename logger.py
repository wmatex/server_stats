#!/usr/bin/python2
# Logs computer temperature and fan speed to database
# Intended to run via cron
from subprocess import check_output
import re
import _mysql
import db

class Logger:
    def __init__(self):
        # TODO: save all this stuff to database
        self._sensors = { 
                'Processor': (1, r'temp1:\s+\+([0-9]+\.[0-9])'),
                'Case': (2, r'M/B Temp:\s+\+([0-9]+\.[0-9])'),
                'Fan': (3, r'fan1:\s+([0-9]+)')
                }
        self._sensors_bin = ["sensors"]
        self._mem = {
                'RAM': (5, r'Mem:\s+([0-9]+).+-/\+ buffers/cache:\s+([0-9]+)')
                }
        self._mem_bin = ["free"]

        self._cpu = {
                'CPU': (4, r'all\s+([0-9]+(?:\.|,)[0-9]+)')
                }
        self._cpu_bin = ["mpstat"]


    def log(self):
        
        try:
            con = _mysql.connect(db.server, db.name, db.password, db.dbname)

            # TODO: implement better parsing
            output = check_output(self._sensors_bin).decode("utf-8")
            for (name, sensor) in self._sensors.items():
                m = re.search(sensor[1], output, re.M)
                if m != None:
                    con.query("INSERT INTO sensor_log(sensor, value) VALUES("+str(sensor[0])+", "+str(m.group(1))+");")

            output = check_output(self._mem_bin).decode("utf-8")
            for (name, mem) in self._mem.items():
                m = re.search(mem[1], output, re.M | re.S)
                if m != None:
                    usage = float(m.group(2))/float(m.group(1))
                    con.query("INSERT INTO sensor_log(sensor, value) VALUES("+str(mem[0])+", "+str(usage)+");")

            output = check_output(self._cpu_bin).decode("utf-8")
            for (name, cpu) in self._cpu.items():
                m = re.search(cpu[1], output, re.M)
                if m != None:
                    con.query("INSERT INTO sensor_log(sensor, value) VALUES("+str(cpu[0])+", "+str(m.group(1))+");")

        except _mysql.Error, e:
            print("MySQL error: %s" % (e.args[1]))

        # finally:
        #     if con:
        #         con.close()



# Main block
if __name__ == "__main__":
    log = Logger()
    log.log()
