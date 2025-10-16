from main.models import Document, ExportBook

def generate_export_book(title,date,school):
    export_book = ExportBook.objects.create(title=title,created_at=date,school=school)
    return export_book

def sss():
    print(1111)
    documents = Document.objects.all()
    for doc in documents:
        if doc.status=='pending':
            generate_export_book(f'Создан документ: {doc.title}',doc.created_at,doc.school)
        elif doc.status=='signed':
            generate_export_book(f'Создан документ: {doc.title}',doc.created_at,doc.school)
            generate_export_book(f'Документ подписан: {doc.title}',doc.created_at,doc.school)
        elif doc.status=='draft':
            generate_export_book(f'Создан черновик: {doc.title}',doc.created_at,doc.school)
            
