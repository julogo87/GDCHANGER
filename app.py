import os
import re
import pdfplumber
from flask import Flask, request, render_template, redirect, url_for, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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
    output_path = pdf_path.replace(".pdf", "_modified.pdf")
    
    with pdfplumber.open(pdf_path) as pdf:
        c = canvas.Canvas(output_path, pagesize=letter)
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                normalized_text = re.sub(r'\s+', ' ', text)
                print("Texto extraído:", normalized_text)
                if old_text in normalized_text:
                    print(f"'{old_text}' encontrado, reemplazando con '{new_text}'.")
                    modified_text = normalized_text.replace(old_text, new_text)
                else:
                    print(f"No se encontró el texto '{old_text}' en la página.")
                    modified_text = normalized_text
                # Añade el texto modificado al nuevo PDF
                text_lines = modified_text.split('\n')
                for i, line in enumerate(text_lines):
                    c.drawString(100, 750 - i*15, line)
                c.showPage()
        c.save()

    return output_path

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

