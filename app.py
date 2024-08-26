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
            output_path = replace_text_in_pdf(file_path, "Tampa Cargo", "Aerounion")
            if output_path:
                return redirect(url_for('download_file', filename=os.path.basename(output_path)))
            else:
                return "No se encontró el texto 'Tampa Cargo' en el documento."
    return render_template('index.html')

def normalize_text(text):
    # Normalizar el texto eliminando puntos, espacios, y saltos de línea
    normalized_text = re.sub(r'[\s\.]+', '', text)
    return normalized_text

def replace_text_in_pdf(pdf_path, old_text, new_text):
    output_path = pdf_path.replace(".pdf", "_modified.pdf")
    doc = fitz.open(pdf_path)
    
    text_found = False
    normalized_old_text = normalize_text(old_text)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        normalized_text = normalize_text(text)
        
        if normalized_old_text in normalized_text:
            text_found = True
            print(f"'{old_text}' encontrado en la página {page_num}.")
            # Aquí puedes continuar con el reemplazo del texto, pero la ubicación exacta puede ser difícil de determinar
            # debido a la normalización. Podrías necesitar un enfoque más avanzado para redibujar el texto.
            
            # Se puede agregar lógica aquí para redibujar o cubrir el texto encontrado y agregar el nuevo texto.
    
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

