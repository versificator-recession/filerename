# Invoice Renamer Webapp

This small Flask web application lets you upload one or more PDF invoices and renames
them automatically using details extracted from the invoice text. It uses the
OpenAI API to identify the invoice date, vendor name and invoice number. The
renamed files are returned in a single ZIP archive.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Export your OpenAI API key:

```bash
export OPENAI_API_KEY=your-key-here
```

3. Run the application:

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.
