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
            output_path = replace_text_in_pdf(file_path, "Tampa Cargo", "AEROUNION")
            if output_path:
                return redirect(url_for('download_file', filename=os.path.basename(output_path)))
            else:
                return "No se encontró el texto 'Tampa Cargo' en el documento."
    return render_template('index.html')

def pattern_match(text):
    # Expresión regular para buscar "Tampa Cargo" con cualquier separador entre letras
    regex = re.compile(r"t\s*\.?\s*a\s*\.?\s*m\s*\.?\s*p\s*\.?\s*a\s*\.?\s*c\s*\.?\s*a\s*\.?\s*r\s*\.?\s*g\s*\.?\s*o", re.IGNORECASE)
    return re.search(regex, text)

def replace_text_in_pdf(pdf_path, old_text, new_text):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    text_found = False

    for page in reader.pages:
        text = page.extract_text()
        if text:
            # Buscar si el patrón se encuentra en la página
            if pattern_match(text):
                text_found = True
                print(f"'{old_text}' encontrado en la página. Reemplazando con '{new_text}'.")
                
                # Aquí se puede implementar lógica adicional para redibujar el texto con PyPDF2 si es necesario
                # Esto es un ejemplo de cómo podríamos proceder con el reemplazo en el texto normalizado.
                modified_text = pattern_match(text).re.sub(new_text, text)
                print("Texto modificado:", modified_text)
            else:
                modified_text = text
            
            # Por ahora, simplemente agregamos la página sin cambios
            # Un reemplazo real en el PDF necesitaría un enfoque diferente
            writer.add_page(page)

    output_path = pdf_path.replace(".pdf", "_modified.pdf")
    with open(output_path, "wb") as output_pdf:
        writer.write(output_pdf)

    if not text_found:
        print("No se encontró el texto 'Tampa Cargo' en el documento.")
        return None

    return output_path

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
