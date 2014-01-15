#!/usr/bin/python2
# Logs various stats from sensors to database
# Intended to run via cron
from subprocess import check_output
import re
import MySQLdb
import MySQLdb.cursors
import db

class Logger:
    def log(self):
        try:
            con = MySQLdb.connect(db.server, db.name, db.password, db.dbname,
                    cursorclass=MySQLdb.cursors.DictCursor)
            cursor = con.cursor()

            # Fetch the settings
            sql = """SELECT p.sensor, p.executable, p.regularExpression, p.groups, p.operators, s.name, s.valueType 
                     FROM parsers p 
                     INNER JOIN sensors s 
                     ON p.sensor = s.id"""
            cursor.execute(sql)
        except Exception, e:
            print("Error: %s" % e)

        # Fetch all rows
        for row in cursor.fetchall():
            try:
                # Capture the output from executable
                output = check_output(row['executable']).decode("utf-8")
                m = re.search(row['regularExpression'], output, re.M | re.S)
                if m != None:
                    value = None
                    if row['groups'] > 1:
                        ops = re.findall(r'\d+|[\./\+-]', row['operators'])
                        value = float(m.group(int(ops[0])))
                        i = 1
                        while i < len(ops):
                            if ops[i] == "+":
                                value += float(m.group(int(ops[i+1])))
                            elif ops[i] == "-":
                                value -= float(m.group(int(ops[i+1])))
                            elif ops[i] == ".":
                                value += str(m.group(int(ops[i+1])))
                            elif ops[i] == "*":
                                value *= float(m.group(int(ops[i+1])))
                            elif ops[i] == "/":
                                value /= float(m.group(int(ops[i+1])))

                            i += 2
                    else:
                        value = float(m.group(1))

                    t = None
                    if row['valueType'] == "float":
                        t = "f"
                    elif row['valueType'] == "int":
                        t = "i"
                    else:
                        t = "s"
                    sql = "INSERT INTO sensor_log(sensor, %svalue) VALUES ('%d', '%s');" % (t.upper(), row['sensor'], value)
                    cursor.execute(sql)
                    con.commit()

            except Exception, e:
                print("Error: %s" % e)

        # finally:
        #     if con:
        #         con.close()


# Main block
if __name__ == "__main__":
    log = Logger()
    log.log()
