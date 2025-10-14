from main.models import Document, ExportBook

docs=Document.objects.all()
print(f"Всего документов: {docs.count()}")