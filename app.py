from flask import Flask, render_template, request, jsonify
import os
from fetchTest import extract_part_titles, extract_section_titles, extract_subtopic_titles, extract_subtopic_content
from datetime import datetime

app = Flask(__name__)

# Path to the PDF directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIRECTORY = os.path.join(PROJECT_DIR, 'bluebook_pdfs')

@app.route('/')
def index():
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
    if request.method == 'POST':
        pdf_file = request.form['pdf_file']
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        # Extract part titles
        part_titles = extract_part_titles(pdf_path)
        return jsonify(part_titles)
    else:
        return jsonify([])

@app.route('/get_section_titles', methods=['POST'])
def get_section_titles():
    if request.method == 'POST':
        pdf_file = request.form['pdf_file']
        part_title = request.form['part_title']
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        # Extract section titles and filter out sections without subsections
        section_titles = extract_section_titles(pdf_path, part_title)
        section_titles = [title for title in section_titles if not title.endswith("[No Subsections]")]
        return jsonify(section_titles)
    else:
        return jsonify([])

@app.route('/get_subsections', methods=['POST'])
def get_subsections():
    if request.method == 'POST':
        pdf_file = request.form['pdf_file']
        section_number = request.form['section_number']
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        # Extract subtopics for the section
        subtopics = extract_subtopic_titles(pdf_path, section_number)
        return jsonify(subtopics)
    else:
        return jsonify([])
    
@app.route('/get_subtopic_content', methods=['POST'])
def get_subtopic_content():
    if request.method == 'POST':
        pdf_file = request.form['pdf_file']
        section_number = request.form['section_number']
        subtopic_number = request.form['subtopic_number']
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        # Extract subtopic content
        subtopic_content = extract_subtopic_content(pdf_path, section_number, subtopic_number)
        return subtopic_content
    else:
        return jsonify({'error': 'Invalid request method'})


if __name__ == '__main__':
    app.run(debug=True)

