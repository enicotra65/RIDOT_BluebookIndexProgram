import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from datetime import datetime
from reference import extract_part, extract_section, extract_subsection
import subprocess

app = Flask(__name__)

# Path to the PDF directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')
STATIC_DIRECTORY = os.path.join(PROJECT_DIR, 'static')
REQUIREMENTS_FILE = os.path.join(PROJECT_DIR, 'requirements.txt')

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    """
    Check if required dependencies are installed. If not, install them from requirements.txt.
    """
    try:
        import flask
        import fitz
        print("All required dependencies are installed.")
        return True
    except ImportError:
        print("Dependencies missing. Installing dependencies...")
        if os.path.exists(REQUIREMENTS_FILE):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
            print("Dependencies installed.")
            return True
        else:
            print("requirements.txt file not found. Unable to install dependencies.")
            return False

def check_and_fetch_bluebooks():
    """
    Check if 'bluebook_pdfs' directory exists. If not, fetch Bluebooks using fetchBluebook.py.
    """
    if not os.path.exists(PDF_DIRECTORY):
        print("'bluebook_pdfs' directory does not exist. Fetching Bluebooks...")
        try:
            subprocess.run([sys.executable, 'fetchBluebook.py'], check=True)
            print("Bluebooks fetched successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to fetch Bluebooks: {e}")
            return False
    else:
        print("Bluebooks are already available.")
        return True

def setup_application():
    """
    Setup application by checking dependencies and fetching Bluebooks if necessary.
    """
    if not check_and_install_dependencies():
        return False
    
    if not check_and_fetch_bluebooks():
        return False
    
    return True

@app.route('/')
def index():
    if not setup_application():
        return "Failed to setup application. Check logs for details."

    # List and prepare PDF files for display
    pdf_files = os.listdir(PDF_DIRECTORY)
    if pdf_files:
        pdf_files_info = []
        for file in pdf_files:
            if file.endswith('.pdf'):
                year, month = file.split('_')
                month_name = datetime.strptime(month[:-4], '%m').strftime('%B')
                pdf_name = f"{month_name}, {year} RIDOT Bluebook"
                pdf_files_info.append({'name': pdf_name, 'file': file})
        return render_template('index.html', pdf_files=pdf_files_info)
    else:
        return "No PDF files found."

@app.route('/get_part_titles', methods=['POST'])
def get_part_titles():
    pdf_file = request.form.get('pdf_file')
    pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
    parts = extract_part(pdf_path)
    return jsonify(parts)

@app.route('/get_sections', methods=['GET'])
def get_sections():
    """
    Endpoint to fetch sections for a selected part in a PDF.
    """
    pdf_selected = request.args.get('pdf_selected')
    part_selected = request.args.get('part_selected')
    pdf_path = os.path.join(PDF_DIRECTORY, pdf_selected)

    sections = extract_section(pdf_path, part_selected)

    # Filter out sections containing "[No Subsections]"
    filtered_sections = [section for section in sections if not section['title'].endswith('[No Subsections]')]

    section_options = ""
    for section in filtered_sections:
        section_options += f"<option value='{section['page_number']}'>{section['title']}</option>"
    
    return section_options

@app.route('/get_subsections', methods=['GET'])
def get_subsections():
    pdf_selected = request.args.get('pdf_selected')
    section_selected = request.args.get('section_selected')
    pdf_path = os.path.join(PDF_DIRECTORY, pdf_selected)

    # Ensure the section_selected is in the correct format
    try:
        section_number = section_selected.split()[1]
    except IndexError:
        return "Invalid section format", 400  # Return a 400 Bad Request error if format is incorrect

    subsections = extract_subsection(pdf_path, section_number)

    subsection_options = ""
    for subsection in subsections:
        subsection_options += f"<option value='{subsection['page_number']}'>{subsection['title']}</option>"

    return subsection_options

@app.route('/pdf_urls.json')
def pdf_urls():
    return send_from_directory(STATIC_DIRECTORY, 'pdf_urls.json')

if __name__ == "__main__":
    if setup_application():
        print("Application setup successfully.")
        app.run(debug=True)
    else:
        print("Application setup failed.")

