import tempfile
import os
from docx import Document as DocxDocument
from docxcompose.composer import Composer
from django.core.files.base import ContentFile

def generate_final_doc(document):
    """
    Обновляет document.file с учётом:
    - school.header_file
    - document.file
    - document.content
    """
    print(document)
    # 1. Берём бланк
    if document.school.headletter:
        base_doc = DocxDocument(document.school.headletter.path)
    else:
        base_doc = DocxDocument()

    composer = Composer(base_doc)

    # 2. Если есть файл у документа
    if document.file:
        user_doc = DocxDocument(document.file.path)
        composer.append(user_doc)

    # 3. Если есть контент
    if document.content:
        text_doc = DocxDocument()
        text_doc.add_paragraph(document.content)
        composer.append(text_doc)

    # 4. Временный файл безопасно создаётся через tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        temp_path = tmp.name

    composer.save(temp_path)

    # 5. Перезаписываем file
    with open(temp_path, "rb") as f:
        document.file.save(f"{document.title}.docx", ContentFile(f.read()), save=True)

    os.remove(temp_path)
    return document
