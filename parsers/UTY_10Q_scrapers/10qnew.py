import os
import json
from bs4 import BeautifulSoup
import time
from colorama import init, Fore
import re


filings_dir = '../data/10QsUTY/'
output_dir = '../data/UTY-Extracted/'
init(autoreset = True) #Set autoreset to True else style configurations would be forwarded to the next print statement


def headers_regex(rows):
    """
    Attempts to find headers that match the pattern:
    '{number} Months Ended {Month} {day}, {year}' in the first few rows.
    This will work for tables with either two or four headers.
    """
    headers = []
    # Regex pattern to match the format: 'Three Months Ended June 30, 2024'
    pattern = r'(\d+)\s+Months\s+Ended\s+(\w+)\s+(\d{1,2}),\s+(\d{4})'

    # Go through the first few rows to locate potential headers
    for row in rows:
        row_text = ' '.join(cell.get_text(strip=True) for cell in row.find_all('td'))
        matches = re.findall(pattern, row_text)

        # Extract headers if pattern matches
        for match in matches:
            number, month, day, year = match
            headers.append(f"{number} Months Ended {month} {day}, {year}")

        # Stop searching once we've found either two or four headers
        if len(headers) == 4:
            break

    # Check if we found the correct number of headers, otherwise return placeholders
    if len(headers) in [2, 4]:
        return headers
    else:
        print("Headers not fully matched; returning placeholders instead.")
        return ["Three Months ended {\P}", "Header 2"] if len(headers) == 2 else ["Header 1", "Header 2", "Header 3", "Header 4"]

def hardstringtoint(text):
    # print(f"Original text: {text}")
    
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


# Updated function to clean row data, ensuring flexibility for different formats
def clean_row(row):
    cleaned_row = []
    for i, cell in enumerate(row):
        if cell == '-' or cell == '—':
            cleaned_row.append(0)
        elif cell == "$":
            # Skip isolated dollar signs
            continue
        elif "(" in cell:  # Handle negative values in parentheses
            cell = cell.replace("(", "-").replace(")", "")
        cell = cell.replace(",", "").replace("$", "").strip()  # Remove commas and any dollar signs
        try:
            cleaned_row.append(int(float(cell)))  # Convert to integer if possible
        except ValueError:
            cleaned_row.append(cell)  # If not a number, keep it as a string
    return cleaned_row



# def extract_results_of_operations(soup):
    # # List of potential key phrases to search for
    # # key_phrases = [
    # #     "Results of Operations",
    # #     "Consolidated Results of Operations",
    # #     "Following are income statement variances for",
    # #     "Operating Results",
    # #     "Income Statement Variances",
    # #     "Results of Operation",
    # #     "Financial Results",
    # #     "Statement of Income",
    # #     "Summary of Results",
    # #     "Management's Discussion and Analysis"
    # #     "Operations Overview",
    # #     "STATEMENT OF INCOME",
    # #     "Statement Of Income",
    # #     "Statements Of Income",
    # #     "CONSOLIDATED STATEMENT OF INCOME AND COMPREHENSIVE INCOME"
    # # ]
    # key_phrases = [
    #     '(unaudited)',
    #     '(Unaudited)',
    #     'CONDENSED',
    #     'Condensed',
    #     'Statement',
    #     'statement'
    #     ]

    
    # for phrase in key_phrases:
    #     results_header = soup.find(string=lambda t: phrase in t)
    #     if results_header:
    #         print(f"'{phrase}' found in document.")
    #         # print(soup.prettify())
            
    #         # Instead of just the first table, let's find all tables nearby
    #         table_candidates = results_header.find_all_next('table')
    #         # print(table_candidates)
            
    #         # Check each table and ensure it has valid numeric content
    #         for idx, table in enumerate(table_candidates):
    #             rows = table.find_all('tr')
    #             if not rows:
    #                 continue  # Skip if the table has no rows

    #             valid_rows = [row for row in rows if row.find_all('td') or row.find_all('th')]
    #             if not valid_rows:
    #                 continue  # Skip empty tables

    #             # Check if the table contains any numeric content
    #             has_numeric_data = any(cell.get_text(strip=True).replace(',', '').replace('(', '').replace(')', '').replace('-', '').isdigit() for row in valid_rows for cell in row.find_all(['th', 'td']))
                
    #             if has_numeric_data:
    #                 header_rows = table.find_all('tr')[:3]  # Assuming first two rows contain headers
    #                 # print(header_rows)
    #                 # Step 2: Concatenate headers from the <td> elements across the three rows
    #                 headers = []
    #                 years = []
    #                 terms = []
    #                 for i, cell in enumerate(header_rows[0].find_all('td')):  # Loop through the first row's cells
    #                     part1 = cell.get_text(strip=True)

    #                     # Check if second and third rows have a corresponding cell
    #                     part2 = header_rows[1].find_all('td')[i].get_text(strip=True) if i < len(header_rows[1].find_all('td')) else ''
    #                     part3 = header_rows[2].find_all('td')[i].get_text(strip=True) if i < len(header_rows[2].find_all('td')) else ''


    #                     if part3 != '' and part2 != '':
    #                         # headers.append(combined_header)
    #                         terms.append(part2)
    #                         years.append(part3)
    #                     # print('intermediate headers: ',headers)

    #                 # Debugging: Print concatenated headers
    #                 for i in terms:
    #                     for j in years:
    #                         headers.append(" ".join([i, j]).strip())
    #                 headers = [header.replace("\xa0", " ").strip() for header in headers]
    #                 print("Concatenated Headers:", headers)
    #                 # print('years: ',years)
    #                 # print('terms:', terms)

    #                 # Step 3: Extract the data rows, starting from the fourth row (after the three header rows)
    #                 data_rows = []
    #                 for row in table.find_all('tr')[3:]:  # Skipping the first three header rows
    #                     data = [td.get_text(strip=True) for td in row.find_all('td')]
    #                     data_rows.append(data)

    #                 # Step 4: Match headers and data into a dictionary
    #                 result = [dict(zip(headers, row)) for row in data_rows]

    #                 # Output result (or save to JSON)
    #                 # print(result)

    #                 print(f"Valid table found with {len(valid_rows)} rows and numeric content.")
    #                 # print(table)
    #                 return headers, table

    #         print(f"Key phrase '{phrase}' found, but no valid table with numeric content found. Skipping...")
    
    # print("No matching header or table found.")
    # return None

def extract_results_of_operations(soup):
    key_phrases = [
        '(unaudited)', '(Unaudited)', 'CONDENSED', 'Condensed', 'Statement', 'statement',
        "Total liabilities",  "Interest expense"
    ]
    
    for phrase in key_phrases:
        results_header = soup.find(string=lambda t: phrase in t)
        if results_header:
            print(f"'{phrase}' found in document.")
            table_candidates = results_header.find_all_next('table')
            
            for idx, table in enumerate(table_candidates):
                rows = table.find_all('tr')
                if not rows:
                    print(f"No rows found in table candidate {idx}. Skipping...")
                    continue

                valid_rows = [row for row in rows if row.find_all('td') or row.find_all('th')]
                has_numeric_data = any(
                    cell.get_text(strip=True).replace(',', '').replace('(', '').replace(')', '').replace('-', '').isdigit()
                    for row in valid_rows for cell in row.find_all(['th', 'td'])
                )
                
                if has_numeric_data:
                    print(f"Valid table found in candidate {idx}. Parsing headers and rows...")

                    # Extract headers from the first three rows
                    header_rows = table.find_all('tr')[:3]
                    headers, years, terms = [], [], []
                    
                    for i, cell in enumerate(header_rows[0].find_all('td')):
                        part1 = cell.get_text(strip=True)
                        part2 = header_rows[1].find_all('td')[i].get_text(strip=True) if i < len(header_rows[1].find_all('td')) else ''
                        part3 = header_rows[2].find_all('td')[i].get_text(strip=True) if i < len(header_rows[2].find_all('td')) else ''
                        
                        print(f"Header parts found: '{part1}', '{part2}', '{part3}'")

                        if part3 and part2:
                            terms.append(part2)
                            years.append(part3)

                    # Combine terms and years to create headers
                    for i in terms:
                        for j in years:
                            headers.append(" ".join([i, j]).strip())
                    headers = [header.replace("\xa0", " ").strip() for header in headers]

                    if not headers:
                        headers = headers_regex(header_rows)

                    print("Concatenated Headers:", headers)


                    # Extract data rows
                    data_rows = []
                    current_subheading = ""
                    for row_index, row in enumerate(table.find_all('tr')[3:]):
                        cells = row.find_all('td')
                        row_data = [td.get_text(strip=True) for td in cells]
                        # print(f"Row {row_index} data: {row_data}")

                        if not any(row_data):
                            print(f"Row {row_index} is empty. Skipping...")
                            continue
                        

                        row_data = clean_row(row_data)
                        # row_data = cleanrow(row_data)
                        # print(f"Row {row_index} data, CLEANED: {row_data}")

                        # # Detect subheadings
                        # if len(row_data) == 1 and not any(cell.isdigit() for cell in row_data):
                        #     current_subheading = row_data[0]
                        #     print(f"Subheading detected: {current_subheading}")
                        #     continue

                        # Clean and store row data
                        if len(row_data) < len(headers):
                            row_data.extend([''] * (len(headers) - len(row_data)))
                            print(f"Row {row_index} extended to match headers: {row_data}")
                        
                        row_key = f"{current_subheading} {row_data[0]}" if current_subheading else row_data[0]

                        row_values = row_data[1:]
                        row_values = [x for x in row_values if x]
                        print(f"Row key: '{row_key}', Row values: {row_values}")
                        
                        data_rows.append((row_key, row_values))

                    print(data_rows)
                    # Compile into structured data
                    result = {}
                    for key, values in data_rows:
                        print('*'*10)
                        print(f'key: {key}')
                        # print(f'headers: {headers}')
                        print(f'values: {values}')
                        values = [x for x in values if x != ')']
                        if not headers:
                            headers = [f'time period {i}' for i in range(len(values))]
                        if len(values) < len(headers) or len(values) == len(headers):
                            row_dict = {headers[i]: values[i] for i in range(len(values))}
                        else:
                            continue

                        # row_dict = {}
                        print(f"Mapping row: {key} -> {row_dict}")
                        result[key] = row_dict
                    
                    return result

            print(f"Key phrase '{phrase}' found, but no valid table with numeric content found. Skipping...")
    
    print("No matching header or table found.")
    return None

# Extract row data as key-value pairs for the dict of dicts
# def parse_filing(file_path):
    # print(f"Parsing file: {file_path}")
    # encodings_to_try = ['utf-8', 'utf-16LE', 'ISO-8859-1', 'latin-1']  # List of encodings to try
    # content = None
    
    # for encoding in encodings_to_try:
    #     try:
    #         with open(file_path, 'r', encoding=encoding) as file:
    #             content = file.read()
    #         print(f"File {file_path} read successfully with {encoding} encoding.")
    #         break  # Exit the loop if successful
    #     except UnicodeDecodeError:
    #         print(f"Unicode error in file {file_path}, attempting to read with {encoding} encoding.")
    
    # if content is None:
    #     print(f"Failed to read file {file_path} with all attempted encodings.")
    #     return None
    
    # # Parse the file content
    # soup = BeautifulSoup(content, 'html.parser')

    # # Extract the "Results of Operations" table
    # headers, table = extract_results_of_operations(soup)

    # if table:
    #     print("Extracting table rows and columns...")
    #     print("Headers detected: ",headers)
    #     rows = table.find_all('tr')
    #     valid_rows = [row for row in rows if row.find_all(['th', 'td'])]  # Filter out empty rows
    #     print(f"Number of valid rows found: {len(valid_rows)}")
    #     if not valid_rows:
    #         print("No valid rows found in the table.")
    #         return None

    #     data = {}
    #     current_subheading = ""

    #     for idx, row in enumerate(valid_rows):
    #         cells = row.find_all(['th', 'td'])
    #         row_data = [cell.get_text(strip=True) for cell in cells]

    #         # Filter out rows that are entirely empty
    #         if not any(row_data):
    #             continue
            
    #         # print(row_data)

    #         # Detect subheadings (e.g., "Operating Revenues:")
    #         if len(row_data) == 1 and not any(cell.isdigit() for cell in row_data):
    #             current_subheading = row_data[0]
    #             continue  # Skip subheading row, but store the subheading

    #         # Ensure row_data matches headers length, fill missing cells if needed
    #         if len(row_data) < len(headers):
    #             row_data.extend([''] * (len(headers) - len(row_data)))

    #         # Use subheading as a prefix for row keys to better organize the data
    #         row_key = f"{current_subheading} {row_data[0]}" if current_subheading else row_data[0]

    #         # Clean up row_data (e.g., handle dollar signs and empty values)
    #         cleaned_row_data = [clean_value(value) for value in row_data]

    #         cleaned_row_data = [x for x in cleaned_row_data if x]


    #         print(cleaned_row_data)

    #         # Map row_data to both "Three Months Ended" and "Six Months Ended" columns
    #         row_dict = {}
    #         for i, header in enumerate(headers):
    #             # if i == 0:
    #             #     continue
    #             if i < len(cleaned_row_data):
    #                 row_dict[header] = cleaned_row_data[i]

    #         data[row_key] = row_dict

    #     return data
    # else:
    #     print(f"No table found in {file_path}")
        # return None


def parse_filing(file_path):
    print(f"Parsing file: {file_path}")
    encodings_to_try = ['utf-8', 'utf-16LE', 'ISO-8859-1', 'latin-1']
    content = None
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            print(f"File {file_path} read successfully with {encoding} encoding.")
            break
        except UnicodeDecodeError:
            print(f"Unicode error in file {file_path}, attempting to read with {encoding} encoding.")
    
    if content is None:
        print(f"Failed to read file {file_path} with all attempted encodings.")
        return None
    
    # Parse the file content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract the "Results of Operations" table
    extracted_data = extract_results_of_operations(soup)

    if extracted_data:
        print("Table extracted successfully.")
        return extracted_data
    else:
        print(f"No valid table found in {file_path}")
        return None


# Function to clean values (e.g., handle $ signs and empty values)
def clean_value(value):
    if value == '$' or value == '':
        return ''  # Remove isolated dollar signs and empty values
    value = value.replace('$', '').replace(',', '')  # Remove $ signs and commas from numbers
    return value.strip()  # Strip excess whitespace


# Function to save data to JSON with the same name as the input file
def save_to_json(data, filename, target_dir):
    try:
        # Ensure the target directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)  # Create directory if it doesn't exist
            print(f"Created output directory: {target_dir}")
        
        # Construct the full file path
        full_path = os.path.join(target_dir, filename)
        
        # Write the data to the file
        with open(full_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Data saved successfully to {full_path}")

    except Exception as e:
        print(f"Error saving data to {filename}: {e}")


others =['10QsSouthern',
          '10QsPSEG',
          '10QsCEG',
          '10QsAEP']

# Main processing loop for directories and files
bigstart = time.time()
for subdir in os.listdir(filings_dir):
     subdir_path = os.path.join(filings_dir, subdir)
     print(subdir)
    
     if os.path.isdir(subdir_path):  # Check if it's a directory
         if subdir in others:
            # print(f"Skipping directory: {subdir}") 
            continue
         print(f"Entering directory: {subdir}")
        
         # Create a corresponding output directory
         output_subdir = os.path.join(output_dir, subdir)
         os.makedirs(output_subdir, exist_ok=True)
        
         # Iterate over files in the subdirectory
         for filename in os.listdir(subdir_path):
             if filename.endswith(".html") or filename.endswith(".htm"):
                 smallstart = time.time()
                 file_path = os.path.join(subdir_path, filename)

                 # Parse the HTML/HTM file and extract the table
                 extracted_table = parse_filing(file_path)
                
                 if extracted_table:
                     json_filename = os.path.splitext(filename)[0] + '_results.json'
                     # Save JSON to the corresponding subdirectory
                     save_to_json(extracted_table, json_filename, output_subdir)
                 else:
                     print(f"Results of Operations table not found in {filename}")
                 print(Fore.GREEN + f"File {filename} in {subdir} processed in {round(time.time()-smallstart,6)} seconds")
     else:
         print(f"Skipping non-directory item: {subdir}")


# extracted = parse_filing('../data/10QsUTY/10QsAEE/aee-20240630.html')
# extracted = parse_filing('../data/10QsUTY/10QsAEE/aee-20240331.html')

# save_to_json(extracted, 'pagggag.json', output_dir)

print(Fore.YELLOW + f"Data extraction completed in {round(time.time()-bigstart,4)} seconds.")

