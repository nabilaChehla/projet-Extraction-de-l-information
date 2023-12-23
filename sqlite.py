import sqlite3
import codecs
import re
import os


if os.path.exists("extraction.db"):
    os.remove("extraction.db")


file = codecs.open(r"corpus-medical_snt\concord.html", "r", "utf-8")

l = file.read()

fin = re.findall("<a[^>]*>(.*?)<\/a>", l)

con = sqlite3.connect("extraction.db")
cur = con.cursor()
cur.execute("CREATE TABLE EXTRACTION ( ID INTEGER PRIMARY KEY, Posologie TEXT )")
i = 1
for x in fin:
    print(f"ID : {i} POSOLOGIE : {x[2]}\n")
    cur.execute(f"INSERT INTO EXTRACTION VALUES ({str(i)},'{x[2]}')")
    i = i + 1

con.commit()
cur.close()
con.close()
