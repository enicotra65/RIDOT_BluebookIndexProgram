import os
import fitz  # PyMuPDF
import re

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



if __name__ == "__main__":
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')
    pdf_files = os.listdir(PDF_DIRECTORY)
    if pdf_files:
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_files[2])
        print("PDF File selected:", pdf_files[2])

        part_titles = extract_part_titles(pdf_path)
        print("Part Titles:")
        for title in part_titles:
            print(title)

        part_title_to_test = part_titles[10]  # Adjust index as needed (Modify Part Number)
        section_titles = extract_section_titles(pdf_path, part_title_to_test)
        print(f"\nSection Titles for {part_title_to_test} :")
        for title in section_titles:
            if "No Subsections" not in title:
                print(title)

        section_title_to_test = section_titles[5]  # Adjust index as needed (Modify Section Number)
        section_number_to_test = section_title_to_test.split()[1]  
        subtopics = extract_subtopic_titles(pdf_path, section_number_to_test)
        print(f"\nSubtopics for {section_title_to_test} :")
        if subtopics:
            for subtopic in subtopics:
                print(subtopic)
        else:
            print(f"No subsections found for {section_title_to_test}")
    else:
        print("No PDF files found in the directory.")
