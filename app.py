import os
import io
import zipfile
from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import openai

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit per file

openai.api_key = os.getenv('OPENAI_API_KEY')

PROMPT = (
    "You are a helpful assistant that extracts invoice details."\
    " Given the text of a PDF invoice, extract the invoice date in MM.DD.YYYY"\
    " format, the vendor name, and the invoice number. Respond in JSON with"\
    " keys 'date', 'vendor', 'number'."
)


def extract_text_from_pdf(file_stream):
    with fitz.open(stream=file_stream.read(), filetype="pdf") as doc:
        text = "\n".join(page.get_text() for page in doc)
    file_stream.seek(0)
    return text


def query_openai(text):
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": text[:4000]},
    ]
    resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    content = resp.choices[0].message.content
    return content


def rename_file(original_filename, details):
    date = details.get("date", "unknown_date")
    vendor = details.get("vendor", "unknown_vendor")
    number = details.get("number", "unknown_number")
    base = f"{date} {vendor} [{number}].pdf"
    return base


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files:
            return render_template('index.html', error='No files uploaded.')

        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in files:
                if not f.filename.lower().endswith('.pdf'):
                    continue
                text = extract_text_from_pdf(f.stream)
                try:
                    response = query_openai(text)
                    details = eval(response)
                except Exception:
                    details = {}
                new_name = rename_file(f.filename, details)
                zipf.writestr(new_name, f.read())
                f.seek(0)
        mem_zip.seek(0)
        return send_file(
            mem_zip,
            download_name='renamed_invoices.zip',
            as_attachment=True
        )
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
