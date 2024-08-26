from flask import Flask, request, render_template, redirect, url_for, send_file
import os
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Verifica y crea el directorio si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file part"
        file = request.files['pdf_file']
        if file.filename == '':
            return "No selected file"
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            output_path = replace_text_in_pdf(file_path, "Tampa Cargo", "Aerounion")
            return redirect(url_for('download_file', filename=os.path.basename(output_path)))
    return render_template('index.html')

def replace_text_in_pdf(pdf_path, old_text, new_text):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        text = page.extract_text()
        text = text.replace(old_text, new_text)
        writer.add_page(page)

    output_path = pdf_path.replace(".pdf", "_modified.pdf")
    with open(output_path, "wb") as output_pdf:
        writer.write(output_pdf)
    
    return output_path

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

