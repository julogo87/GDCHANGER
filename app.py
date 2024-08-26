import os
import re
import fitz  # PyMuPDF
from flask import Flask, request, render_template, redirect, url_for, send_file

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

def replace_text_in_pdf(pdf_path, old_text, new_text):
    doc = fitz.open(pdf_path)
    output_path = pdf_path.replace(".pdf", "_modified.pdf")
    text_found = False

    # Expresión regular para buscar "Tampa Cargo" con cualquier separador entre letras
    pattern = re.compile(r"t\s*\.?\s*a\s*\.?\s*m\s*\.?\s*p\s*\.?\s*a\s*\.?\s*c\s*\.?\s*a\s*\.?\s*r\s*\.?\s*g\s*\.?\s*o", re.IGNORECASE)

    for page in doc:
        text_instances = page.search_for(old_text)
        
        if text_instances:
            text_found = True
            for inst in text_instances:
                # Añadir anotación de redacción
                page.add_redact_annot(inst, fill=(255, 255, 255))
                page.apply_redactions()
                # Ajustar la posición del texto bajándolo una línea (ajustar coordenada Y)
                adjusted_position = (inst[0], inst[1] + 8)  # Baja 10 unidades la posición vertical
                page.insert_text(adjusted_position, new_text, fontsize=inst[3]-inst[1], color=(0, 0, 0))

    if text_found:
        doc.save(output_path)
        return output_path
    else:
        doc.close()
        return None

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
