import sqlite3
import codecs
import re
import os

if os.path.exists("extraction.db"):
    os.remove("extraction.db")

file = codecs.open(r"corpus-medical_snt\concord.html", "r", "utf-8")
content = file.read()
file.close()

# utiliser set pour avoir des valeurs uniques :
unique_posologies = set()

# extraire le contenues des balise <a></a>
pattern = re.compile(r"<a[^>]*>(.*?)<\/a>")

matches = pattern.findall(content)

con = sqlite3.connect("extraction.db")
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS EXTRACTION (ID INTEGER PRIMARY KEY, Posologie TEXT)"
)

#  Ordonner les valeurs par alphabet pour insérer :
sorted_posologies = sorted(set(matches), key=lambda x: x.lower())

for i, posologie in enumerate(sorted_posologies, start=1):
    print(f"ID: {i} POSOLOGIE: {posologie}\n")
    cur.execute("INSERT INTO EXTRACTION (ID, Posologie) VALUES (?, ?)", (i, posologie))

con.commit()
cur.close()
con.close()
