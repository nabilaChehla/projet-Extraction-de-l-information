import sys
import os
import re

# Fonction qui vérifie si une ligne marque le début d'un bloc d'informations médicales.
def block_start(line):
    line = line.strip().lower()
    starters = {
        "Traitement hospitalier",
        "Prescription(s) médicale(s) de médicaments",
        "Type de Stomie",
        "Traitement de sortie",
        "Le traitement de sortie comporte",
        "TRAITEMENT MEDICAL DE SORTIE",
        "TRAITEMENT À DOMICILE",
        "Le traitement médical associe",
        "Son traitement actuel comporte",
        "Traitement:",
    }
    starters = [starter.lower() for starter in starters]

    for starter in starters:
        if starter in line:
            return True

    return False

# Fonction qui extrait les blocs d'informations médicales d'un fichier.
def extract_blocks():
    with open("corpus-medical.txt", "r", encoding="utf-8") as file:
        content = file.readlines()

    in_block = False
    blocks = []
    current_block = []

    for line in content:
        if block_start(line):
            in_block = True
            current_block.append(line)
        elif in_block:
            current_block.append(line)
            if (
                line == "\n"
                or "Aucun" in line
                or "aucun" in line
                or "Histoire de la maladie" in line
                or "Examen clinique à l’entrée :" in line
                or "Mode de vie" in line
                or "Bilan paraclinique" in line
                or "Examen clinique" in line
                or "CENTRE HOSPITALIER UNIVERSITAIRE" in line
                or "Pas de modification" in line
                or "Le patient reviendra" in line
                or "Restant à" in line
            ):
                in_block = False
                blocks.append("".join(current_block))
                current_block = []

    for line in content:
        if line.startswith("TAD :"):
            in_block = True
            current_block.append(line)
        elif in_block:
            current_block.append(line)
            if "." in line:
                in_block = False
                blocks.append("".join(current_block))
                current_block = []

    return blocks

# Fonction qui supprime certains fichiers s'ils existent déjà.
def delete_existing_files():
    for file_name in ["info2", "info3", "subst_corpus.dic"]:
        if os.path.exists(file_name):
            os.remove(file_name)

# Fonction qui charge les médicaments existants à partir d'un fichier.
def load_existing_medications(file_path):
    existing_medications = set()

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-16le") as file:
            for line in file:
                medication_name = line.split(",")[0]
                existing_medications.add(medication_name.strip())

    return existing_medications

# Fonction qui extrait les noms de médicaments du corpus médical en utilisant des expressions régulières.
def extract_medication_names_corpus(text):
    medication_names = []

    pattern = r"traitement par ([A-Za-z{alph}]{4,})( et ([A-Za-z{alph}]{4,}))?"

    matches = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)

    for match in matches:
        group1 = match.group(1)
        group2 = match.group(3)
        medication_names.extend([group1, group2])

    medication_names = list(filter(None, medication_names))

    # exlude some results :
    medication_names = [med.lower() for med in medication_names]

    element_non_medicament = {
        "anti","drogues","injection","posologie",
    }

    medication_names = [
        med for med in medication_names if (med not in french_words and med not in element_non_medicament)
    ]

    return list(set(medication_names))

# Fonction qui extrait les noms de médicaments des blocs d'informations médicales en utilisant des expressions régulières.
def extract_medication_names_blocks(text):
    medication_names = []

    pattern = r"\b([A-Za-z{alph}]{5,})(?=\s*(jusqu’à|en seringue))|([A-Z]{5,})(?=(,|\.|\n))|([A-Za-z{alph}]{5,})(\s?LP)?\s*(\d+(,\d+)?)(?!.*\s*(ui\/h|cc)\b)(?:mg|g|ml)?|([A-Za-z{alph}]{5,})(\s?LP)?\s*(\d+(\s\d+)?)(?=.*\/j)|([A-Za-z{alph}]{4,})(?: ?\s*:\s*\d*\s*(fois|cp|midi|\/j))"

    matches = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)

    for match in matches:
        group1 = match.group(1)
        group2 = match.group(3)
        group3 = match.group(5)
        group4 = match.group(10)
        group5 = match.group(14)
        medication_names.extend([group1, group2, group3, group4, group5])

    medication_names = list(filter(None, medication_names))

    # exlude some results :
    medication_names = [med.lower() for med in medication_names]
    element_non_medicament = {
        "orale","doses","juillet","sandrine","dossiermed","valider","perfusion","derivations","posologie","ampoule","biologie","constantes","mardi","injection","oxygène","neurologie","vanille"
    }
    medication_names = [
        med for med in medication_names if (med not in french_words and med not in element_non_medicament)
    ]

    return list(set(medication_names))

# Fonction qui trie les lignes d'un fichier par ordre alphabétique.
def sort_file_by_line(filename, encoding="utf-8"):
    try:
        with open(filename, "r", encoding=encoding) as file:
            content = file.read()

        if content.startswith("\ufeff"):
            bom = "\ufeff"
            content = content.replace("\ufeff", "")
        else:
            bom = ""

        lines = content.splitlines()

        sorted_lines = sorted(lines)

        with open(filename, "w", encoding=encoding) as file:
            file.write(bom)
            file.write("\n".join(sorted_lines))


    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Fonction qui remplit deux fichiers avec des statistiques sur les nouveaux médicaments.
def fill_info_files(stats_file_2, stats_file_3, letters, new_medications_unique, enrichier_medicaments):
    total2 = 0
    total3 = 0

    with open(stats_file_2, "w", encoding="utf-8") as file_2, open(
        stats_file_3, "w", encoding="utf-8"
    ) as file_3:
        for letter in letters:
            count_corpus = 0
            count_total = 0
            for med in new_medications_unique:
                if med.lower().startswith(letter):
                    file_2.write(f"{med.lower()}\n")
                    count_corpus += 1
                    total2 += 1

            for med in enrichier_medicaments:
                if med.lower().startswith(letter):
                    file_3.write(f"{med.lower()}\n")
                    count_total += 1
                    total3 += 1

            file_2.write("------------------------------------\n\n\n")
            file_2.write(f"{letter}: {count_corpus}")
            file_2.write("\n\n\n------------------------------------\n")
            file_3.write("------------------------------------\n\n\n")
            file_3.write(f"{letter}: {count_total}\n")
            file_3.write("\n\n\n------------------------------------\n")

        file_2.write(f"\nTotal: {total2}\n")
        file_3.write(f"\nTotal: {total3}\n")

# Fonction qui retourne l'alphabet français.
def getFR_Alphabet():
    alph_file = open("Alphabet.txt", "r", encoding="utf-16-le")
    alph = ""
    for line in alph_file:
        alph = alph + line
    return alph

# Fonction qui charge un ensemble de mots français à partir d'un fichier.
def load_french_words(dictionary_file):
    french_words = set()

    with open(dictionary_file, "r", encoding="utf-16-le") as f:
        for line in f:
            word = line.split(",")[0]
            french_words.add(word)
    return french_words

# Fonction qui supprime les éléments d'une liste d'une autre liste.
def remove_list1_from_list2(list2, list1):
    return [word for word in list2 if word not in list1]

# Chargement des mots français à partir du fichier "dlf".
french_words = load_french_words("dlf")

# Fonction principale du script.
def main():
    delete_existing_files()
    alph = getFR_Alphabet()

    if len(sys.argv) != 2:
        print("Usage: python enrichir.py <corpus_medical_file_path>")
        sys.exit(1)

    corpus_medical_file_path = sys.argv[1]
    subst_dic_path = "subst.dic"
    subst_corpus_path = "subst_corpus.dic"

    existing_medications = load_existing_medications(subst_dic_path)

    blocks = extract_blocks()

    with open(corpus_medical_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    new_medications = extract_medication_names_corpus(content)

    text = ""
    for block in blocks:
        text += block

    new_medications.extend(extract_medication_names_blocks(text))
    new_medications.sort()

    # Remove duplicates from new_medications
    new_medications_unique = list(dict.fromkeys(new_medications))

    # -MEDICAMENT ENRICHI : ----------------------------------------------------
    enrichier_medicaments = [
        enrichier_med
        for enrichier_med in new_medications_unique
        if enrichier_med not in existing_medications
    ]
    enrichier_medicaments = list(dict.fromkeys(enrichier_medicaments))
    enrichier_medicaments.sort()

    # -----------------------------------------------------------------------------
    with open(subst_dic_path, "r", encoding="utf-16le") as file:
        content = file.read()

    letters = re.findall(r"^\s*(\b[a-z]{1})", content, re.MULTILINE)
    letters = list(dict.fromkeys(letters))
    letters.sort()

    # -----------------------------------------------------------------------------

    with open(subst_dic_path, "a", encoding="utf-16le") as subst_dic_file:
        for medication in new_medications_unique:
            for letter in letters:
                if medication.lower().startswith(letter):
                    subst_dic_file.write(f"{medication.lower()},.N+subst\n")

    sort_file_by_line(subst_dic_path, "utf-16le")

    # Write new medications (with duplicates) to subst_corpus.dic
    with open(subst_corpus_path, "w", encoding="utf-16le") as subst_corpus_file:
        subst_corpus_file.write("\ufeff")

        for medication in new_medications:
            for letter in letters:
                if medication.lower().startswith(letter):
                    subst_corpus_file.write(f"{medication.lower()},.N+subst\n")

    stats_file_2 = "infos2.txt"
    stats_file_3 = "infos3.txt"

    fill_info_files(
        stats_file_2,
        stats_file_3,
        letters,
        new_medications_unique,
        enrichier_medicaments,
    )

    print("Enrichment terminee.")

# Exécution de la fonction principale si le script est lancé directement.
if __name__ == "__main__":
    main()
