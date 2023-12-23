import re
import sys
import requests
import os
from unidecode import unidecode


def extract_medication_names(html_content):
    # Define regular expressions for extracting medication names
    medication_pattern = re.compile(r"<a href=\"Substance/[^>]+\">([^<]+)</a>")

    # Find all matches for medication names
    medications = medication_pattern.findall(html_content)

    return medications


def main():
    # Delete existing files if they exist
    delete_files = ["subst.dic", "infos1.txt"]

    for file_name in delete_files:
        if os.path.exists(file_name):
            os.remove(file_name)

    if len(sys.argv) != 3:
        print("Usage: python extraire.py <page_range> <http_port>")
        print("Example: python extraire.py B-H 8080")
        sys.exit(1)

    page_range = sys.argv[1]
    http_port = sys.argv[2]

    # Validate and extract the start and end letters from the page range
    if len(page_range) != 3 or page_range[1] != "-":
        print(
            "Invalid page range format. Please use the format B-H, E-S, A-W, or A-Z, etc."
        )
        sys.exit(1)

    start_letter = page_range[0].upper()
    end_letter = page_range[2].upper()

    # Generate a list of URLs based on the specified page range and XAMPP setup
    base_url = (
        f"http://127.0.0.1:{http_port}/vidal/vidal-Sommaires-Substances-{{letter}}.html"
    )
    urls = [
        base_url.format(letter=chr(letter))
        for letter in range(ord(start_letter), ord(end_letter) + 1)
    ]

    # Create an empty list to store all medications
    all_medications = []

    # Process each URL in the specified range
    for url in urls:
        # Use requests to fetch HTML content from the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            response.encoding = "utf-8"
            html_content = response.text

            # Extract medication names from the HTML content
            medications = extract_medication_names(html_content)

            # Add the medications to the list
            all_medications.extend(medications)
        else:
            print(f"Failed to access URL: {url}")

    # Write the medications to a .dic file with UTF-16 LE encoding and BOM
    output_file_path = "subst.dic"
    with open(output_file_path, "w", encoding="utf-16le") as output_file:
        # Write BOM (Byte Order Mark) for UTF-16 LE
        output_file.write("\ufeff")
        # Update the medication dictionary
        for medication in all_medications:
            # Ensure correct encoding and handle non-ASCII characters
            output_file.write(f"{medication},.N+subst\n")

    print(f"{output_file_path} is written")

    # Generate statistics and write to infos1.txt
    alphabet_counts = {chr(letter): 0 for letter in range(ord("A"), ord("Z") + 1)}
    total_count = 0

    for medication in all_medications:
        first_letter = medication[0].upper()
        normalized_letter = unidecode(first_letter)
        # So we can treat the case of caracters like é
        if normalized_letter in alphabet_counts:
            alphabet_counts[normalized_letter] += 1
            total_count += 1
    # Write statistics to infos1.txt
    stats_file_path = "infos1.txt"
    with open(stats_file_path, "w", encoding="utf-8") as stats_file:
        for letter, count in alphabet_counts.items():
            stats_file.write(f"{letter}: {count}\n")

        stats_file.write(f"Total: {total_count}\n")

    print(f"Statistics have been written to {stats_file_path}")
    print(f"HTTP port: {http_port}")


if __name__ == "__main__":
    main()
