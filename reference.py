import os
import fitz  # PyMuPDF
import re
import json
from datetime import datetime

# Determine the path to the PDF directory relative to the current file
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')

def extract_part(pdf_path):
    """
    Extracts the titles of the parts from the PDF's table of contents.

    Args:
    pdf_path (str): Path to the PDF file.

    Returns:
    list: A list of dictionaries containing part titles and their respective page numbers.
    """
    part_info = []
    with fitz.open(pdf_path) as doc:
        toc = doc.get_toc()
        for item in toc:
            if re.match(r'^Part [0-9A-Z]+', item[1]):  # Check if the entry starts with "Part" followed by a number or a letter
                part_info.append({'title': item[1], 'page_number': item[2]})
    return part_info

def extract_section(pdf_path, part_title):
    """
    Extracts the section titles for a specified part from the PDF's table of contents.
    
    Args:
    pdf_path (str): Path to the PDF file.
    part_title (str): The title of the part for which sections need to be extracted.
    
    Returns:
    list: A list of dictionaries containing section titles and their respective page numbers under the specified part.
    """
    section_info = []
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
                        section_info.append({'title': section_title, 'page_number': toc[end_index][2]})
                    end_index += 1
                break
    return section_info

    

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



def extract_subsection(pdf_path, section_number):
    """
    Extracts the titles of subtopics for a specified section from the PDF.
    Args:
    pdf_path (str): Path to the PDF file.
    section_number (str): The number of the section for which subtopic titles need to be extracted.
    Returns:
    list: A list of dictionaries containing subsection titles and their page numbers.
    """
    subtopic_info = []
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
                            subtopic_info.append({
                                'title': subtopic_title,
                                'page_number': page_num + 1  # Page numbers are 1-based index in PyMuPDF
                            })
                    else:
                        # Continue collecting subtopics if the title starts with at least two capital letters
                        if re.match(r'^[A-Z][A-Z].*$', line.split(maxsplit=1)[1]):
                            subtopic_title = line.rstrip('.')
                            subtopic_info.append({
                                'title': subtopic_title,
                                'page_number': page_num + 1  # Page numbers are 1-based index in PyMuPDF
                            })
    return subtopic_info



if __name__ == "__main__":
    pdf_files = os.listdir(PDF_DIRECTORY)
    if pdf_files:

        # Define the path to your PDF and the page number you want to test
        # Make sure to use the correct path to your PDF file
        pdf_selected = pdf_files[0]  # Adjust index as needed to select PDF
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_selected)

        # Extract parts
        parts = extract_part(pdf_path)
        
        # Display all part titles with their corresponding page numbers
        print("Part Titles and Page Numbers:")
        for part in parts:
            print(f"- Part Title: {part['title']}, Page Number: {part['page_number']}")
        
        # Select the first part
        part_index = 0  # Change this index to select a different part
        part_selected = parts[part_index]
        print(f"\nSelected Part: {part_selected['title']}")
        
        # Extract sections under the selected part
        sections = extract_section(pdf_path, part_selected['title'])
        
        # Display all section titles with their corresponding page numbers (filtered)
        print("\nSection Titles and Page Numbers (Filtered):")
        for section in sections:
            if not section['title'].endswith("[No Subsections]"):
                print(f"- Section Title: {section['title']}, Page Number: {section['page_number']}")
        
        # Select a section index for the selected part
        section_index = 0  # Change this index to select a different section
        
        # Assuming section_index is correctly defined
        if section_index < len(sections):
            section_selected = sections[section_index]
            print(f"\nSelected Section: {section_selected['title']}")
    
            # Extract subsections under the selected section
            section_number = section_selected['title'].split()[1]
            subsections = extract_subsection(pdf_path, section_number)
    
            # Display all subsection titles with their corresponding page numbers
            print("\nSubsection Titles and Page Numbers:")
            for subsection in subsections:
                print(f"- Subsection Title: {subsection['title']}, Page Number: {subsection['page_number']}")
        else:
            print(f"\nInvalid section index {section_index}. No section found.")