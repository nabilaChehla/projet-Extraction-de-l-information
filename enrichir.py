import sys
import os
import re


def delete_existing_files():
    # Delete info2, info3, and subst_corpus.dic if they exist
    for file_name in ["info2", "info3", "subst_corpus.dic"]:
        if os.path.exists(file_name):
            os.remove(file_name)


def load_existing_medications(file_path):
    existing_medications = set()

    # Load existing medications from subst.dic file
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-16le") as file:
            for line in file:
                medication_name = line.split(",")[0]
                existing_medications.add(medication_name.strip())

    return existing_medications


import re


def extract_medication_names(text):
    medication_names = []

    # Read the alphabet from a file
    with open("Alphabet.txt", "r", encoding="utf-16-le") as alph_file:
        alphFR = alph_file.read().strip()

        # Exclude '\n' from the alphabet
    alphFR = alphFR.replace("\n", "")

    # Define a regular expression pattern to capture only drug names
    pattern = rf"^\s*(\d*-)?\b([A-Za-z{alphFR}]+)(\s?LP)?\s*(\d+\s?\d*\.?\,?\s?\d*)\s(?:mg|ml|µg|mcg|g|cp|µg|l|mmol|UI)|(^\b[A-Za-z{alphFR}]+)(\s?LP)?\s*(\d+\s?\d*\.?\,?\s?\d*)\s(?:mg|ml|µg|mcg|g|cp|µg|l|mmol|UI)|^\b([A-Za-z{alphFR}]+)(\s?LP)?\s?(\d+\s?\d*\.?\,?\s?\d*)\s?:?\s?\d*\s?le?\s(?:matin|midi|soir)|^-?\s?(\b[A-Za-z{alphFR}]+)\s:?\s?(\d+\s?\d*\.?\,?\s?\d*)\s(?:mg|ml|µg|mcg|g|cp|µg|l|mmol|UI)|\s(\b[A-Za-z{alphFR}]+)\sà\s(\d+\s?\d*\.?\,?\s?\d*)\s?$"

    # Find all matches in the text using re.DOTALL flag
    matches = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)

    # Iterate over matches and append specific groups to the list
    for match in matches:
        group1 = match.group(2)  # Second capturing group of the first alternative
        group2 = match.group(5)  # First capturing group of the second alternative
        group3 = match.group(8)  # First capturing group of the third alternative
        group4 = match.group(11)  # First capturing group of the fourth alternative
        medication_names.extend([group1, group2, group3, group4])

    # Filter out None values (in case a group did not match in a particular iteration)
    medication_names = list(filter(None, medication_names))

    # Remove meidcation names that are less than 4 characters long
    medication_names = [med for med in medication_names if len(med) > 3]
    # exlude some results :
    element_non_medicament = {
        "Diurèse",
        "Oxygénothérapie",
        "Posologie",
        "Oxygène",
        "puis",
        "TcPO",
    }

    medication_names = [
        med for med in medication_names if med not in element_non_medicament
    ]

    return medication_names


# ----------------------------------------------------------------------------------
def has_bom(content):
    # Check for UTF-8 BOM
    return content.startswith("\ufeff")


def sort_file_by_line(filename, encoding="utf-8"):
    try:
        # Read the content of the file
        with open(filename, "r", encoding=encoding) as file:
            content = file.read()

        # Check for BOM and save it for later
        bom = "\ufeff" if has_bom(content) else ""

        # Split the content into lines
        lines = content.splitlines()

        # Sort the lines alphabetically
        sorted_lines = sorted(lines)

        # Write the sorted lines back to the file
        with open(filename, "w", encoding=encoding) as file:
            # Write BOM if necessary
            file.write(bom)
            file.write("\n".join(sorted_lines))

        print(f"File '{filename}' has been sorted alphabetically.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# ----------------------------------------------------------------------------------
def main():
    delete_existing_files()

    if len(sys.argv) != 2:
        print("Usage: python enrichir.py <corpus_medical_file_path>")
        sys.exit(1)

    corpus_medical_file_path = sys.argv[1]
    subst_dic_path = "subst.dic"
    subst_corpus_path = "subst_corpus.dic"

    # Load existing medications from subst.dic file
    existing_medications = load_existing_medications(subst_dic_path)

    # Open corpus-medical.txt file to extract new medications

    with open(corpus_medical_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract potential medication names from the medical corpus
    Extracted_medications = extract_medication_names(content)

    # Remove duplicates from     Extracted_medications
    Extracted_medications_unique = list(set(Extracted_medications))
    print(Extracted_medications_unique)
    print(len(Extracted_medications_unique))
    # -MEDICAMENT ENRICHI : ----------------------------------------------------
    enrichier_medicaments = [
        enrichier_med.strip().lower()
        for enrichier_med in Extracted_medications
        if enrichier_med.strip().lower() not in existing_medications
    ]

    enrichier_medicaments.sort()
    enrichier_medicaments_unique = list(set(enrichier_medicaments))
    # -----------------------------------------------------------------------------
    # Append new medications to subst.dic
    with open(subst_dic_path, "a", encoding="utf-16le") as subst_dic_file:
        for medication in Extracted_medications_unique:
            if medication not in existing_medications:
                subst_dic_file.write(f"{medication.lower()},.N+subst\n")

    # Sort subst.dic
    sort_file_by_line("subst.dic", "utf-16le")

    # Write new medications (with duplicates) to subst_corpus.dic
    with open(subst_corpus_path, "w", encoding="utf-16le") as subst_corpus_file:
        # Write BOM (Byte Order Mark) for UTF-16 LE
        subst_corpus_file.write("\ufeff")

        for medication in Extracted_medications:
            subst_corpus_file.write(f"{medication.lower()},.N+subst\n")

    stats_file_2 = "infos2.txt"
    stats_file_3 = "infos3.txt"

    with open(stats_file_2, "w", encoding="utf-8") as file_2, open(
        stats_file_3, "w", encoding="utf-8"
    ) as file_3:
        for letter in "abcdefghijklmnopqrstuvwxyz":
            count_corpus = 0
            count_total = 0
            for med in Extracted_medications_unique:
                if med.lower().startswith(letter):
                    file_2.write(f"{med.lower()}\n")
                    count_corpus += 1

            for med in enrichier_medicaments_unique:
                if med.lower().startswith(letter):
                    file_3.write(f"{med.lower()}\n")
                    count_total += 1

            file_2.write("------------------------------------\n\n\n")
            file_2.write(f"{letter}: {count_corpus}")
            file_2.write("\n\n\n------------------------------------\n")
            file_3.write("------------------------------------\n\n\n")
            file_3.write(f"{letter}: {count_total}\n")
            file_3.write("\n\n\n------------------------------------\n")

        file_2.write(f"\nTotal: {len(Extracted_medications_unique)}\n")
        file_3.write(f"\nTotal: {len(enrichier_medicaments_unique)}\n")

    print("Enrichment process completed.")


if __name__ == "__main__":
    main()
