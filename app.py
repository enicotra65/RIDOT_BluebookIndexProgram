from flask import Flask, render_template, request, jsonify
import os
from fetchTest import fetch_part_titles, fetch_section_titles, fetch_subtopics
from datetime import datetime

app = Flask(__name__)

# Determine the path to the PDF directory relative to the current file
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')

@app.route('/')
def index():
    # List PDF files in the directory
    pdf_files = os.listdir(PDF_DIRECTORY)
    if pdf_files:
        # Extract month and year from PDF file names and create PDF names
        pdf_files_info = []
        for file in pdf_files:
            if file.endswith('.pdf'):
                year, month = file.split('_')
                month_name = datetime.strptime(month[:-4], '%m').strftime('%B')  # Remove .pdf extension
                pdf_name = f"{month_name}, {year} RIDOT Bluebook"
                pdf_files_info.append({'name': pdf_name, 'file': file})
        # Pass PDF files to the template
        return render_template('index.html', pdf_files=pdf_files_info)
    else:
        return "No PDF files found in the directory."

@app.route('/get_part_titles', methods=['POST'])
def get_part_titles():
    if request.method == 'POST':
        pdf_file = request.form['pdf_file']
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        # Fetch part titles for the selected PDF
        part_titles = fetch_part_titles(pdf_path)
        return jsonify(part_titles)
    else:
        return jsonify([])  # Return an empty list if not a POST request

@app.route('/get_section_titles', methods=['POST'])
def get_section_titles():
    if request.method == 'POST':
        pdf_file = request.form['pdf_file']
        part_title = request.form['part_title']
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        # Fetch section titles for the selected part
        section_titles = fetch_section_titles(pdf_path, part_title)
        # Filter out sections without subsections
        section_titles = [title for title in section_titles if not title.endswith("[No Subsections]")]
        return jsonify(section_titles)
    else:
        return jsonify([])  # Return an empty list if not a POST request

@app.route('/get_subsections', methods=['POST'])
def get_subsections():
    if request.method == 'POST':
        pdf_file = request.form['pdf_file']
        section_number = request.form['section_number']
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        # Fetch subtopics for the selected section
        subtopics = fetch_subtopics(pdf_path, section_number)
        return jsonify(subtopics)
    else:
        return jsonify([])  # Return an empty list if not a POST request


if __name__ == '__main__':
    app.run(debug=True)
