import os

# Vérifie si le répertoire existe et le supprime s'il est présent
if os.path.exists("corpus-medical_snt"):
    os.system("rd /S corpus-medical_snt")

os.mkdir("corpus-medical_snt")
# Normalise le texte en utilisant Norm.txt
os.system("UnitexToolLogger Normalize corpus-medical.txt -r Norm.txt")
# Tokenise le texte normalisé en utilisant le fichier d'alphabet spécifié "Alphabet.txt"
os.system("UnitexToolLogger Tokenize corpus-medical.snt -a Alphabet.txt")

os.system("UnitexToolLogger Compress subst.dic")
os.system(
    "UnitexToolLogger Dico -t corpus-medical.snt -a Alphabet.txt Dela_fr.bin subst.bin"
)
os.system("UnitexToolLogger Grf2Fst2 posologie.grf")

# Applique le transducteur FST2 au texte tokenisé en utilisant "Alphabet.txt"
os.system(
    "UnitexToolLogger Locate -t corpus-medical.snt posologie.fst2 -a Alphabet.txt -L -I --all"
)
os.system(
    'UnitexToolLogger Concord corpus-medical_snt/concord.ind -f "Courier new" -s 12'
)

# -----------------------------------------------------------------------------------------
# Utilité de alphabet.txt:
# ----------------------------------------------------------------------------------------
"""
- on utilise alphabet.txt pour ordonner les tokens par ordre alphabetique 
et avoir le nombre d'occurances pour chaque ensemble de lettres équivalentes 
"""
