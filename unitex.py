import os

# Vérifie si le répertoire existe et le supprime s'il est présent
if os.path.exists("corpus-medical_snt"):
    os.system("rd /S corpus-medical_snt")

os.mkdir("corpus-medical_snt")
# Normalise le texte et crée un fichier de normalisation "Norm.txt"
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
""" Lors du Tokenisation (pretraitement), on liste les tokens par ordre alphabetique
donc si on a un 'é' par exemple on doit le considerer equivalent a un 'e' juste pour pouvoir 
le classé dans la liste ordonné dess tokens, cette information se trouve au nivreau de alphabet.txt"""


# pour spécifier comment les caractères sont traités et analysés. Il définit l'ensemble de caractères
# ou l'alphabet utilisé dans les tâches de traitement linguistique, assurant ainsi la cohérence et
# la précision de l'analyse du corpus médical.
