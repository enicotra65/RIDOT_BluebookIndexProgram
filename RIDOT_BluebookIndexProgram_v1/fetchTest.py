import os
import fitz  # PyMuPDF
import re
from datetime import datetime

# Determine the path to the PDF directory relative to the current file
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')


def extract_part_titles(pdf_path):
    """
    Extracts the titles of the parts from the PDF's table of contents.

    Args:
    pdf_path (str): Path to the PDF file.

    Returns:
    list: A list of part titles found in the PDF.
    """
    part_titles = []
    with fitz.open(pdf_path) as doc:
        toc = doc.get_toc()
        for item in toc:
            if re.match(r'^Part [0-9A-Z]+', item[1]):  # Check if the entry starts with "Part" followed by a number or a letter
                part_titles.append(item[1])
    return part_titles


def extract_section_titles(pdf_path, part_title):
    """
    Extracts the section titles for a specified part from the PDF's table of contents.
    Args:
    pdf_path (str): Path to the PDF file.
    part_title (str): The title of the part for which sections need to be extracted.
    Returns:
    list: A list of section titles under the specified part.
    """
    section_titles = []
    with fitz.open(pdf_path) as doc:
        toc = doc.get_toc()  
        part_regex = re.compile(r'^Part [0-9A-Z]+')  
        for item in toc:
            if item[1] == part_title:  
                start_index = toc.index(item)  
                end_index = start_index + 1
                while end_index < len(toc) and not part_regex.match(toc[end_index][1]):
                    if toc[end_index][1].startswith("SECTION"):
                        section_title = toc[end_index][1]
                        has_subsections = contains_subsections(doc, toc, end_index)
                        if not has_subsections:
                            section_title += " [No Subsections]"
                        section_titles.append(section_title)
                    end_index += 1
                break
    return section_titles


def contains_subsections(doc, toc, section_index):
    """
    Checks if a section has subsections by examining the table of contents.
    Args:
    doc (fitz.Document): The PDF document object.
    toc (list): Table of contents of the PDF.
    section_index (int): Index of the current section in the TOC.
    Returns:
    bool: True if subsections are found, False otherwise.
    """
    section_page = toc[section_index][2]
    end_page = doc.page_count
    if section_index + 1 < len(toc):
        for i in range(section_index + 1, len(toc)):
            if re.match(r'^Part \d+', toc[i][1]):
                break
            if toc[i][1].startswith("SECTION"):
                end_page = toc[i][2] - 1
                break
    for page_num in range(section_page - 1, end_page):
        page_text = doc.load_page(page_num).get_text("text")
        if re.search(r'\d+\.\d+', page_text):  # Simple pattern to identify subsections (e.g., 1.1, 1.2, etc.)
            return True
    return False


def extract_subtopic_titles(pdf_path, section_number):
    """
    Extracts the titles of subtopics for a specified section from the PDF.
    Args:
    pdf_path (str): Path to the PDF file.
    section_number (str): The number of the section for which subtopic titles need to be extracted.
    Returns:
    list: A list of subtopic titles under the specified section.
    """
    subtopic_titles = []
    first_subsection_found = False
    subsection_pattern = rf'^{section_number}\.\d+\s[A-Z].*$'
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page_text = doc.load_page(page_num).get_text("text")
            lines = page_text.split("\n")
            combined_lines = []
            # Combine lines where the section number and title are separated by a newline
            for i in range(len(lines)):
                if re.match(rf'^{section_number}\.\d+$', lines[i].strip()):
                    if i + 1 < len(lines) and re.match(r'^[A-Z]', lines[i + 1].strip()):
                        combined_lines.append(lines[i].strip() + " " + lines[i + 1].strip())
                        continue
                combined_lines.append(lines[i].strip())
            for line in combined_lines:
                match = re.match(subsection_pattern, line)
                if match:
                    if not first_subsection_found:
                        # Start collecting subtopics from .01 onwards where the title starts with at least two capital letters
                        if re.match(rf'^{section_number}\.01\s+[A-Z][A-Z].*$', line):
                            first_subsection_found = True
                            subtopic_title = line.rstrip('.')
                            subtopic_titles.append(subtopic_title)
                    else:
                        # Continue collecting subtopics if the title starts with at least two capital letters
                        if re.match(r'^[A-Z][A-Z].*$', line.split(maxsplit=1)[1]):
                            subtopic_title = line.rstrip('.')
                            subtopic_titles.append(subtopic_title)
    return subtopic_titles


def extract_subtopic_content(pdf_path, section_number, subtopic_number):
    """
    Extracts the content for a specified subtopic from the PDF.

    Args:
    pdf_path (str): Path to the PDF file.
    section_number (str): The number of the section containing the subtopic.
    subtopic_number (str): The number of the subtopic for which content needs to be extracted.

    Returns:
    str: The content of the specified subtopic.
    """
    subtopic_content = ""
    subtopic_pattern = rf'^{section_number}\.{subtopic_number}\s+[A-Z][A-Za-z].*?$'
    next_subtopic_pattern = rf'^{section_number}\.(\d+)\s+[A-Z][A-Za-z].*?$'

    try:
        with fitz.open(pdf_path) as doc:
            start_extracting = False
            for page_num in range(len(doc)):
                page_text = doc.load_page(page_num).get_text("text")
                lines = page_text.split("\n")
                combined_lines = []

                # Combine lines where the subtopic number and title are separated by a newline
                for i in range(len(lines)):
                    if re.match(rf'^{section_number}\.\d+$', lines[i].strip()):
                        if i + 1 < len(lines) and re.match(r'^[A-Z]', lines[i + 1].strip()):
                            combined_lines.append(lines[i].strip() + " " + lines[i + 1].strip())
                            continue
                    combined_lines.append(lines[i].strip())

                for line in combined_lines:
                    if re.match(subtopic_pattern, line):
                        start_extracting = True
                        continue  # Skip the line matching the subtopic title

                    if start_extracting:
                        # Stop collecting content if the next subtopic title is encountered
                        if re.match(next_subtopic_pattern, line):
                            start_extracting = False
                            break
                        subtopic_content += line + "\n"
    except Exception as e:
        print("Error:", e)
        subtopic_content = "Error occurred while processing the document."

    #process raw text to be formatted
    final_text = format_text(subtopic_content, pdf_path, section_number)

    return final_text


def format_text(raw_text, pdf_path, section_number):
    """
    Formats the raw text by removing date and page numbers, part titles, section titles, 
    adding newlines before bullet points and lettered lists, and formatting acronyms and abbreviations.

    Args:
    raw_text (str): The raw text to be formatted.
    pdf_path (str): Path to the PDF file for extracting date.
    section_number (str): The number of the section containing the subtopic.

    Returns:
    str: The formatted text.
    """
    # Extract date from filename
    pdf_filename = os.path.basename(pdf_path)
    base_filename = os.path.splitext(pdf_filename)[0]
    match = re.match(r'(\d{4})_(\d{2})', base_filename)
    if match:
        year, month = match.groups()
        date_string = datetime.strptime(f"{year}_{month}", "%Y_%m").strftime("%B %Y")
    else:
        date_string = ""

    # Determine the current part number
    current_part_number = section_number[0] + "00" if section_number[0].isdigit() else section_number[0]

    # Define regex patterns
    patterns_to_remove = [
        rf'{date_string}',
        rf'{current_part_number}-\d{{1,2}}',
        rf'Part\s+{current_part_number}\s+—\s+.*$',
        rf'SECTION\s+{section_number}\s+—\s+.*$',
    ]
    
    # Compile the patterns
    compiled_patterns = [re.compile(pattern, flags=re.MULTILINE) for pattern in patterns_to_remove]
    
    # Function to apply all patterns
    def remove_patterns(text, patterns):
        for pattern in patterns:
            text = pattern.sub('', text)
        return text

    # Apply the patterns
    filtered_text = remove_patterns(raw_text, compiled_patterns)
    
    # Additional text processing steps
    transformations = [
        (r'\n{2,}', '\n\n'),                                        # Removes large amounts of white space caused by page breaks
        (r'\n\n', '\n'),                                            # Removes unnecessary newlines at the start of a new page
        (r'([•●○])\s*', r'\1 '),                                    # Adjusts bullet points to be on the same line as the text following them
        #(r'([A-Z]{2,})\n\s*([A-Z][^\n]+)', r'\1 - \2'),            # Formats acronyms and abbreviations with a hyphen
        (r'\n([a-z]\.)', r'\n\n\1'),                                # Adds newlines before lettered lists
        (r'^.*\.{6,}.*$', '', re.MULTILINE),                        # Removes TOC title with following periods (assuming it's at the beginning or end)
        (r'([•●○])\s*', r'\n\t\1 ', re.MULTILINE),                  # Indents wrapped lines under bullet points
        (r'\n\t([^\n]+)', r'\n\t\1', re.MULTILINE),                 # Indents subsequent lines after the indented bullet point  
        (r"(?<!\b)\n(?=[A-Z][^.!?\s]*?\b)", r"\n\n", re.MULTILINE), # Adds a newline inbetween all lines that have a \n followed by a Capital Letter (excluding bullet points)
        (r"\n\t○", r"\n\t\t\t○", re.MULTILINE),
    ]
    
    # Apply the transformations
    for pattern, replacement, *flags in transformations:
        filtered_text = re.sub(pattern, replacement, filtered_text, flags=flags[0] if flags else 0)
        print("After regex transformations:", filtered_text)  # Print intermediate result

    
    # Stop at the next section or part title
    next_section_pattern = rf'SECTION\s+\d+.*'
    next_part_pattern = rf'Part\s+\d+.*'
    stop_pattern = rf'({next_section_pattern}|{next_part_pattern})'
    split_text = re.split(stop_pattern, filtered_text)
    filtered_text = split_text[0] if split_text else filtered_text

    return filtered_text.strip()



if __name__ == "__main__":
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))   # Get program path
    PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs') # Get PDF directory path
    pdf_files = os.listdir(PDF_DIRECTORY)                      # Get PDF List
    if pdf_files:

        #Get PDFs
        pdf_selected = pdf_files[2]                          # Adjust index as needed to select PDF
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_selected) # Fetch PDF File path
        
        #Get Parts
        part_titles = extract_part_titles(pdf_path) # Fetch part titles
        part_selected = part_titles[10]             # Adjust index as needed (Modify Part Number)
        
        #Get Sections
        section_titles = extract_section_titles(pdf_path, part_selected) # Fetch Section Titles from selected part

        #Get Subtopics
        section_selected = section_titles[0]                                   # Adjust index as needed (Modify Section Number)
        section_selected_number = section_selected.split()[1]                  # Extract section number from section selected
        subtopics = extract_subtopic_titles(pdf_path, section_selected_number) # Fetch Subtopic Titles

        #Get Formatted Content
        section_number = "M01"                                                                 # Adjust section number as needed
        subtopic_number = "01"                                                                 # Adjust subtopic number as needed
        subtopic_content = extract_subtopic_content(pdf_path, section_number, subtopic_number) # Fetch subtopic Content 

        print("PDF File selected:", pdf_selected) # PDF Selection Output

        print("Part Titles:") # Part Selection Output
        for title in part_titles:
            print(title)

        print(f"\nSection Titles for {part_selected} :") # Fetched Section Title Output
        for title in section_titles:
            if "No Subsections" not in title:
                print(title)

        print(f"\nSubtopics for {section_selected} :") # Fetched Subtopic Title Output
        if subtopics:
            for subtopic in subtopics:
                print(subtopic)
        else:
            print(f"No subsections found for {section_selected}")

        print("Content for subtopic", section_number + "." + subtopic_number, ":", subtopic_content) #Fetched Subtopic Content (Formatted) Output
    else:
        print("No PDF files found in the directory.")