import re
import sys
import requests
import os
from unidecode import unidecode


def extraire_noms_medicaments(contenu_html):
    # Définir les expressions régulières pour extraire les noms des médicaments
    motif_medicament = re.compile(r"<a href=\"Substance/[^>]+\">([^<]+)</a>")

    # Trouver toutes les correspondances pour les noms des médicaments
    medicaments = motif_medicament.findall(contenu_html)

    return medicaments


def principal():
    # Supprimer les fichiers existants s'ils existent
    fichiers_a_supprimer = ["subst.dic", "infos1.txt"]

    for nom_fichier in fichiers_a_supprimer:
        if os.path.exists(nom_fichier):
            os.remove(nom_fichier)

    if len(sys.argv) != 3:
        print("Utilisation : python extraire.py <plage_pages> <port_http>")
        print("Exemple : python extraire.py B-H 8080")
        sys.exit(1)

    plage_pages = sys.argv[1]
    port_http = sys.argv[2]

    # Valider et extraire la lettre de début et de fin de la plage des pages
    if len(plage_pages) != 3 or plage_pages[1] != "-":
        print(
            "Format de plage de pages invalide. Veuillez utiliser le format B-H, E-S, A-W, ou A-Z, etc."
        )
        sys.exit(1)

    lettre_debut = plage_pages[0].upper()
    lettre_fin = plage_pages[2].upper()

    # Générer une liste d'URLs basée sur la plage de pages spécifiée et la configuration XAMPP
    base_url = (
        f"http://127.0.0.1:{port_http}/vidal/vidal-Sommaires-Substances-{{lettre}}.html"
    )
    urls = [
        base_url.format(lettre=chr(lettre))
        for lettre in range(ord(lettre_debut), ord(lettre_fin) + 1)
    ]

    # Créer une liste vide pour stocker tous les médicaments
    tous_les_medicaments = []

    # Traiter chaque URL dans la plage spécifiée
    for url in urls:
        # Utiliser requests pour récupérer le contenu HTML de l'URL
        reponse = requests.get(url)

        # Vérifier si la requête a réussi (code d'état 200)
        if reponse.status_code == 200:
            reponse.encoding = "utf-8"
            contenu_html = reponse.text

            # Extraire les noms des médicaments du contenu HTML
            medicaments = extraire_noms_medicaments(contenu_html)

            # Ajouter les médicaments à la liste
            tous_les_medicaments.extend(medicaments)
        else:
            print(f"Échec d'accès à l'URL : {url}")

    # Écrire les médicaments dans un fichier .dic avec un encodage UTF-16 LE et un BOM
    chemin_fichier_sortie = "subst.dic"
    with open(chemin_fichier_sortie, "w", encoding="utf-16le") as fichier_sortie:
        # Écrire le BOM (Byte Order Mark) pour UTF-16 LE
        fichier_sortie.write("\ufeff")
        # Mettre à jour le dictionnaire des médicaments
        for medicament in tous_les_medicaments:
            # Assurer une encodage correcte et gérer les caractères non-ASCII
            fichier_sortie.write(f"{medicament},.N+subst\n")

    print(f"{chemin_fichier_sortie} est rempli")

    # Générer des statistiques et écrire dans infos1.txt
    compte_alphabet = {chr(lettre): 0 for lettre in range(ord("A"), ord("Z") + 1)}
    total_compte = 0

    for medicament in tous_les_medicaments:
        premiere_lettre = medicament[0].upper()
        lettre_normalisee = unidecode(premiere_lettre)
        # Afin de traiter les cas de caractères comme é
        if lettre_normalisee in compte_alphabet:
            compte_alphabet[lettre_normalisee] += 1
            total_compte += 1
    # Écrire les statistiques dans infos1.txt
    chemin_fichier_stats = "infos1.txt"
    with open(chemin_fichier_stats, "w", encoding="utf-8") as fichier_stats:
        for lettre, compte in compte_alphabet.items():
            fichier_stats.write(f"{lettre}: {compte}\n")

        fichier_stats.write(f"Total : {total_compte}\n")

    print(f"Statistiques remplies dans : {chemin_fichier_stats}")
    print(f"Port HTTP : {port_http}")


# Exécuter la fonction principale si le script est lancé directement
if __name__ == "__main__":
    principal()
