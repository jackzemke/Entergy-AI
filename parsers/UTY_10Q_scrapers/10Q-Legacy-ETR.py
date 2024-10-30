import os
import json
from bs4 import BeautifulSoup
import time
from colorama import init, Fore


filings_dir = '../data/10QHTML/'
output_dir = '../data/10Q-Extracted/'
init(autoreset=True)  # Prevents style from being forwarded in print stataments


def hardstringtoint(text):

    # Handle dashes or empty text
    if text == '-' or text == '—':
        return 0

    # Remove commas, parentheses, and dollar signs
    text = text.replace(",", '')
    if "(" in text:
        text = text.replace("(", '-')
        text = text.replace(")", '')
    text = text.replace("$", '')

    try:
        return int(float(text))
    except ValueError:
        print(f"Failed to convert: {text}")
        return text  # Return the original text if conversion fails


def pardig(text):
    has_number = False
    has_parenthesis = False
    for k in text:
        if k.isdigit():
            has_number = True
        elif k == '(' or k == ')':
            has_parenthesis = True

    return has_number and has_parenthesis


def cleanrow(row):
    for i in range(len(row)):
        if i == 0:
            continue  # Skip the first column (assuming it's the row key)

        if pardig(row[i]):
            row[i] = hardstringtoint(row[i])
            continue

        for j in row[i]:
            if j.isdigit():
                row[i] = hardstringtoint(row[i])
                break

        # Handle dashes and empty values
        if row[i] == '-' or row[i] == '—':
            row[i] = hardstringtoint(row[i])
            continue

        # Handle incomplete parentheses entries
        if row[i] == '(' or row[i] == ')':
            row[i] = ''

    return list(filter(None, row))  # Filter out any remaining empty strings


# Key headings to help identify the header row
key_headings = ['Utility', 'Parent &Other (a)', 'Entergy']


def extract_results_of_operations(soup):
    # List of potential key phrases to search for
    key_phrases = [
        "Results of Operations",
        "Following are income statement variances for",
        "Operating Results",
        "Income Statement Variances",
        "Results of Operation",
        "Operations Overview"
    ]

    for phrase in key_phrases:
        results_header = soup.find(string=lambda t: phrase in t)
        if results_header:
            print(f"'{phrase}' found in document.")
            table = results_header.find_next('table')
            if table:
                return table

    print("No matching header or table found.")
    return None

# Extract row data as key-value pairs for the dict of dicts
def parse_filing(file_path):
    print(f"Parsing file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        print(
            f"Unicode error in file {file_path},"
            f"attempting to read with utf-16LE encoding.")
        with open(file_path, 'r', encoding='utf-16LE') as file:
            content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Extract the "Results of Operations" table
    table = extract_results_of_operations(soup)

    if table:
        print("Extracting table rows and columns...")
        data = {}
        rows = table.find_all('tr')

        # Dynamically determine the header row and data rows
        headers = []
        for idx, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            row_data = [cell.get_text(strip=True) for cell in cells]

            # Assume the first non-empty row is the header
            if len(headers) == 0:
                if any(row_data):
                    headers = row_data
                    headers = list(filter(None, headers))
                    print(f"Headers detected: {headers}")
                continue

            # Extract row data as key-value pairs for the dict of dicts
            row_key = row_data[0] if row_data else ""
            if row_key:
                row_data = cleanrow(row_data)

                # Ensure the row_data length matches the headers
                if len(row_data) < len(headers):
                    print(
                        Fore.RED + f"Warning: Mismatch between "
                        f"row_data and headers length for {row_key}")
                    print(f"Data: {row_data}")
                    print(f"Headers: {headers}")
                    continue

                # Correctly map row_data to headers
                row_dict = {headers[i]: row_data[i] for i in range(
                    1, len(headers)) if i < len(row_data)}
                # print(f"Row Key: {row_key}, Values: {row_dict}")

                data[row_key] = row_dict
            else:
                # print(f"Skipped empty row")
                pass

        return data
    else:
        print(f"No 'Results of Operations' table found in {file_path}")
        return None


# Function to save data to JSON with the same name as the input file
def save_to_json(data, filename, target_dir):
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)
    # Construct the full file path
    full_path = os.path.join(target_dir, filename)
    with open(full_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


# Main processing loop
bigstart = time.time()
for filename in os.listdir(filings_dir):
    if filename.endswith(".html") or filename.endswith(".htm"):
        smallstart = time.time()
        file_path = os.path.join(filings_dir, filename)

        # Parse the HTML/HTM file and extract the table
        extracted_table = parse_filing(file_path)

        if extracted_table:
            json_filename = os.path.splitext(filename)[0] + '_results.json'
            # Specify the target directory here
            save_to_json(extracted_table, json_filename, output_dir)
        else:
            print(f"Results of Operations table not found in {filename}")
        print(
            Fore.GREEN + f"File {filename} processed in"
            f" {round(time.time()-smallstart, 6)} seconds")

print(Fore.YELLOW +
      f"Data extraction completed in {round(time.time()-bigstart,4)} seconds.")
