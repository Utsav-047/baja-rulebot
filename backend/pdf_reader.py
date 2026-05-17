import pdfplumber
import io

def extract_text_from_pdf(file):
    content = file.read()
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    print(f"Total characters extracted: {len(text)}")
    return text