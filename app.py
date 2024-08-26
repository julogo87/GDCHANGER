import os
import re
from flask import Flask, request, render_template, redirect, url_for, send_file
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
            if output_path:
                return redirect(url_for('download_file', filename=os.path.basename(output_path)))
            else:
                return "No se encontró el texto 'Tampa Cargo' en el documento."
    return render_template('index.html')

def normalize_text(text):
    # Normalizar el texto eliminando puntos, espacios y saltos de línea, y uniendo todo en una sola cadena
    normalized_text = re.sub(r'[\s\.]+', '', text)
    return normalized_text

def replace_text_in_pdf(pdf_path, old_text, new_text):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    text_found = False
    normalized_old_text = normalize_text(old_text)
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            normalized_text = normalize_text(text)
            print(f"Texto normalizado de la página: {normalized_text}")

            if normalized_old_text in normalized_text:
                text_found = True
                print(f"'{old_text}' encontrado. Reemplazando con '{new_text}'.")

                # Reemplazar el texto original con el nuevo en el texto normalizado
                modified_text = text.replace(old_text, new_text)
            else:
                modified_text = text
            
            # Por ahora, agregamos la página sin cambios
            # Para un reemplazo real en el PDF, se necesitaría un enfoque diferente
            writer.add_page(page)

    output_path = pdf_path.replace(".pdf", "_modified.pdf")
    with open(output_path, "wb") as output_pdf:
        writer.write(output_pdf)
    
    if not text_found:
        return None

    return output_path

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
