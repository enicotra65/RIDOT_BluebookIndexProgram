import os
import fitz  # PyMuPDF
import re

# Determine the path to the PDF directory relative to the current file
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')

def fetch_part_titles(pdf_path):
    """
    Fetches the titles of the parts in the PDF.

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

def fetch_section_titles(pdf_path, part_title):
    """
    Fetches the section titles for a specified part in the PDF, marking those without subsections.

    Args:
    pdf_path (str): Path to the PDF file.
    part_title (str): The title of the part for which sections need to be fetched.

    Returns:
    list: A list of section titles under the specified part with a flag for sections without subsections.
    """
    section_titles = []
    with fitz.open(pdf_path) as doc:
        toc = doc.get_toc()  # Get the table of contents
        part_regex = re.compile(r'^Part [0-9A-Z]+')  # Match part titles with numbers or letters
        for item in toc:
            if item[1] == part_title:  # Find the specified part title
                start_index = toc.index(item)  # Get the index of the part title
                end_index = start_index + 1
                # Collect section titles until the next part is encountered
                while end_index < len(toc) and not part_regex.match(toc[end_index][1]):
                    if toc[end_index][1].startswith("SECTION"):
                        section_title = toc[end_index][1]
                        # Check if there are subsections
                        has_subsections = check_for_subsections(doc, toc, end_index)
                        if not has_subsections:
                            section_title += " [No Subsections]"
                        section_titles.append(section_title)
                    end_index += 1
                break
    return section_titles


def check_for_subsections(doc, toc, section_index):
    """
    Checks if a section has subsections by looking ahead in the table of contents.

    Args:
    doc (fitz.Document): The PDF document object.
    toc (list): Table of contents of the PDF.
    section_index (int): Index of the current section in the TOC.

    Returns:
    bool: True if subsections are found, False otherwise.
    """
    # Starting page of the current section
    section_page = toc[section_index][2]
    end_page = doc.page_count
    # Determine the end page for the current section by checking the next section or part
    if section_index + 1 < len(toc):
        for i in range(section_index + 1, len(toc)):
            if re.match(r'^Part \d+', toc[i][1]):
                break
            if toc[i][1].startswith("SECTION"):
                end_page = toc[i][2] - 1
                break
    
    # Look for subsection markers within the pages of the section
    for page_num in range(section_page - 1, end_page):
        page_text = doc.load_page(page_num).get_text("text")
        if re.search(r'\d+\.\d+', page_text):  # Simple pattern to identify subsections (e.g., 1.1, 1.2, etc.)
            return True
    return False




def fetch_subtopics(pdf_path, section_number):
    """
    Fetches the subtopics for a specified section in the PDF.

    Args:
    pdf_path (str): Path to the PDF file.
    section_number (str): The number of the section for which subtopics need to be fetched.

    Returns:
    list: A list of subtopics under the specified section.
    """
    subtopics = []
    first_subsection_found = False
    subsection_pattern = rf'^{section_number}\.\d+\s[A-Z].*$'

    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page_text = doc.load_page(page_num).get_text("text")  # Get text from the page
            lines = page_text.split("\n")
            for line in lines:
                line = line.strip()
                match = re.match(subsection_pattern, line)
                if match:
                    if not first_subsection_found:
                        # Only accept the first subsection if it ends with .01
                        if re.match(rf'^{section_number}\.01\s', line):
                            first_subsection_found = True
                            subtopic = line.rstrip('.')
                            subtopics.append(subtopic)
                    else:
                        subtopic = line.rstrip('.')
                        subtopics.append(subtopic)

    if not subtopics:
        print(f"No subsections found for SECTION {section_number}")
    return subtopics


if __name__ == "__main__":
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')
    pdf_files = os.listdir(PDF_DIRECTORY)
    if pdf_files:
        # Select the first PDF file
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_files[2])
        print("PDF File selected:", pdf_files[2])

        # Fetch and print part titles
        part_titles = fetch_part_titles(pdf_path)
        print("Part Titles:")
        for title in part_titles:
            print(title)

        # Test fetching section titles for a specific part (e.g., Part 100)
        part_title_to_test = part_titles[10]  # Adjust index as needed
        section_titles = fetch_section_titles(pdf_path, part_title_to_test)
        print(f"\nSection Titles for {part_title_to_test} :")
        for title in section_titles:
            if "No Subsections" not in title:
                print(title)

        # Test fetching subtopics for a specific section (e.g., SECTION 101)
        section_title_to_test = section_titles[5]  # Adjust index as needed
        section_number_to_test = section_title_to_test.split()[1]  # Extract the section number (e.g., 102)
        subtopics = fetch_subtopics(pdf_path, section_number_to_test)
        print(f"\nSubtopics for {section_title_to_test} :")
        if subtopics:
            for subtopic in subtopics:
                print(subtopic)
        else:
            print(f"No subsections found for {section_title_to_test}")
    else:
        print("No PDF files found in the directory.")



