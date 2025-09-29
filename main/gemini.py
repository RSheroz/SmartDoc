import requests, json, base64, win32com.client
from docx import Document

api_key = "AIzaSyBSiqzxih_ra6_qhiL7shCaQGvpKsTigGw"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

def convert_doc_to_docx_windows(doc_path):
    word = win32com.client.Dispatch("Word.Application")
    doc = word.Documents.Open(doc_path)
    docx_path = doc_path + "x"
    doc.SaveAs(docx_path, FileFormat=16)  # 16 = wdFormatDocumentDefault (docx)
    doc.Close()
    word.Quit()
    return docx_path

def read_docx_with_tables(file):
    doc = Document(file)
    full_text = []

    # Текст из параграфов
    for para in doc.paragraphs:
        full_text.append(para.text)

    # Таблицы
    for table in doc.tables:
        full_text.append("\n[Таблица]")
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            full_text.append(" | ".join(cells))  # можно заменить на CSV-стиль
        full_text.append("[Конец таблицы]\n")

    return "\n".join(full_text)

def chatgpt(prompt):
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt+", ответ выводить без стилизации"}
                ]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    except:
        return '<div class="alert alert-danger">Error connection or request</div>'

    result = response.json()
    text = result['candidates'][0]['content']['parts'][0]['text']
    return text

def send_file(file_paths, prompt):
    file_contents = []
    for f in file_paths:
        if f.endswith('.docx'):
            with open(f, 'rb') as file:
                file_contents.append(read_docx_with_tables(file))
        else:
            return "Файлҳо бояд формати docx дошта бошанд."
    file_contents = "----начало нового файла----".join(file_contents)
    return chatgpt(prompt + file_contents)