from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as llogout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .forms import *
from .gemini import *
from .models import *
from .append_headletter import generate_final_doc   # импортируем функцию генерации DOCX
from .permissions import *
import os, uuid, re, docx, datetime, main.tt
# Регистрация шрифта DejaVu для поддержки кириллицы
font_path = os.path.join(settings.BASE_DIR, 'main', 'static', 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', font_path))
# 

def add_export_book(title, school):
    export_book = ExportBook.objects.create(title=title, school=school)
    # return export_book

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user, request.POST['password'])
        if user is not None or User.objects.filter(username=username).exists():
            # Проверка одобрения школы для директоров и админов
            if user.school and not user.school.approved:
                messages.error(request, "Ваша школа ещё не одобрена администрацией.")
                return redirect('login')

            login(request, user)

            # Перенаправление по ролям
            if user.is_superuser:
                return redirect('smartadmin:dashboard')
            elif user.role == 'director':
                return redirect('index')
        else:
            messages.error(request, "Неверный логин или пароль.")
    return render(request, 'main/login.html')
    
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'main/register.html'
    success_url = reverse_lazy('user_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        # Только супер-админ и директор могут менять роль
        if not (user.is_superuser or user.role == 'director'):
            form.fields.pop('role', None)
        return form

    def get_object(self, queryset=None):
        obj = get_object_or_404(User, pk=self.kwargs['pk'])

        # 1️⃣ Суперадмин — может редактировать всех
        if self.request.user.is_superuser:
            return obj

        # 2️⃣ Директор — только пользователей своей школы
        if getattr(self.request.user, 'role', None) == 'director':
            if obj.school == self.request.user.school:
                return obj
            else:
                raise PermissionDenied("Вы можете редактировать только пользователей своей школы.")

        # 3️⃣ Остальные — только себя
        if obj == self.request.user:
            return obj

        raise PermissionDenied("У вас нет прав для редактирования этого пользователя.")

    def get_queryset(self):
        # для безопасности (чтобы не показать других в select)
        qs = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return qs  # все пользователи
        elif getattr(user, 'role', None) == 'director':
            return qs.filter(school=user.school)
        else:
            return qs.filter(pk=user.pk)

    # ✅ Вот сюда добавляем redirect to back
    def get_success_url(self):
        # 1️⃣ сначала пробуем параметр next из URL
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return next_url

        # 2️⃣ затем пробуем Referer
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            return referer

        # 3️⃣ если ничего нет — возвращаем в список пользователей
        return reverse_lazy('user_list')
    
class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'main/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    def get_queryset(self):
        return User.objects.filter(school=self.request.user.school)
class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'main/document_form.html'
    success_url = reverse_lazy('documents')

    def form_valid(self, form):
        response = super().form_valid(form)
        add_export_book(f"Обновлён документ: {self.object.title}", self.request.user.school)
        return response

class DocumentDeleteView(DeleteView):
    model = Document
    template_name = 'main/document_delete.html'
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        add_export_book(f"Удалён документ: {self.object.title}", self.request.user.school)
        return super().delete(request, *args, **kwargs)

class TemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'main/template_form.html'
    success_url = reverse_lazy('templates')

    def get_queryset(self):
        return Template.objects.filter(school=self.request.user.school)

    def form_valid(self, form):
        response = super().form_valid(form)
        add_export_book(f"Обновлён шаблон: {self.object.title}", self.request.user.school)
        return response

class TemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = Template
    template_name = 'main/template_confirm_delete.html'
    success_url = reverse_lazy('templates')

    def get_queryset(self):
        return Template.objects.filter(school=self.request.user.school)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        add_export_book(f"Удалён шаблон: {self.object.title}", self.request.user.school)
        return super().delete(request, *args, **kwargs)

@login_required
def index(request):
    docs = Document.objects.filter(school=request.user.school).order_by('-created_at')
    templates = Template.objects.filter(school=request.user.school)
    stat = docs.aggregate(
        pending=Count('id', filter=Q(status='pending')),
        signed=Count('id', filter=Q(status='signed'))
    )
    data = {
        'docs': docs,
        'templates': templates,
        'stat': stat,
    }
    return render(request, 'main/index.html', data)


@login_required
def user_list(request):
    users = User.objects.filter(school=request.user.school)
    return render(request, 'main/user_list.html', {'users': users})

def school_reg(request):
    if request.method == "POST":
        form = SchoolRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Заявка успешно отправлена! Ожидайте подтверждения.")
            return redirect("login")
        else:
            messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = SchoolRegistrationForm()
    return render(request, 'main/school_reg.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'main/profile.html', {'form': form})


def add_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})


def logout(request):
    llogout(request)
    return redirect('login')


@login_required
def templates(request):
    templates = Template.objects.filter(school=request.user.school)
    return render(request, 'main/templates.html', {"templates": templates})

@login_required
def categories(request):
    categories = Category.objects.all()
    return render(request, 'main/categories.html', {"categories": categories})

@login_required
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    documents = Document.objects.filter(category=category, school=request.user.school)
    return render(request, 'main/category_detail.html', {
        'category': category,
        'documents': documents
    })

@login_required
def download_category_archive(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    documents = Document.objects.filter(category=category, school=request.user.school)

    from io import BytesIO
    import zipfile
    from django.http import HttpResponse

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc in documents:
            # Добавить текстовый файл с содержимым
            zip_file.writestr(f"{doc.title}.txt", doc.content)
            # Если есть файл, добавить его
            if doc.file:
                zip_file.write(doc.file.path, f"{doc.title}_{doc.file.name}")

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{category.name}_documents.zip"'
    return response

@login_required
def template_create(request):
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.school = request.user.school
            template.save()
            add_export_book(f"Создан шаблон: {template.title}", request.user.school)
            return redirect('templates')
    else:
        form = TemplateForm()
    return render(request, 'main/template_form.html', {'form': form})


@login_required
def documents(request):
    documents = Document.objects.filter(school=request.user.school)
    templates = Template.objects.filter(school=request.user.school)
    users = User.objects.filter(school=request.user.school)
    data = {'documents': documents, 'templates': templates, 'users': users}
    return render(request, 'main/documents.html', data)


@login_required
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.created_by = request.user
            doc.school = request.user.school
            doc.save()
            add_export_book(f"Создан документ: {doc.title}", request.user.school)
            if request.POST.get('leadletter'):  # если чекбокс отмечен
                # generate_final_doc(doc)  # сборка финального DOCX
                pass
            return redirect('documents')
        else:
            print(form.errors)
    else:
        form = DocumentForm()
    return render(request, 'main/document_form.html', {'form': form})


@login_required
def fill_template(request, id):
    data = {}
    template_text = Template.objects.get(id=id)
    data['title'] = template_text.title + f'{datetime.datetime.now().strftime(" %d.%m.%Y")}'
    template_text_content = template_text.content
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        res = template_text_content
        for k, v in request.POST.items():
            if k != 'csrfmiddlewaretoken':
                res = re.sub(r'\{\{\s*' + re.escape(k) + r'\s*\}\}', v, res)
        data['res'] = res
        data['form'] = form
    else:
        def replace_var(match):
            var_name = match.group(1)
            return f'<input type="text" class="fill" name="{var_name}" placeholder="{var_name}">'
        rendered_text = re.sub(r'\{\{\s*([\wа-яА-яёЁ\-]+)\s*\}\}', replace_var, template_text_content)
        data['data'] = rendered_text
    return render(request, 'main/fill_template.html', data)


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    data = {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "status": document.status if hasattr(document, 'status') else None,
        "category": document.category.name if document.category else None,
        "status_display": document.get_status_display() if hasattr(document, 'get_status_display') else None,
        "created_by_name": document.created_by.username if document.created_by else None,
        "file": document.file.url if document.file else None,
        "created_at": document.created_at,
    }
    return JsonResponse(data, safe=False)

@login_required
def document_view(request, pk):
    document = get_object_or_404(Document, pk=pk, school=request.user.school)
    return render(request, 'main/document_view.html', {'document': document})

@login_required
def school(request):
    school = request.user.school
    users = User.objects.filter(school=school)
    documents = Document.objects.filter(school=school)
    templates = Template.objects.filter(school=school)
    data = {
        'school': school,
        'users': users,
        'documents': documents,
        'templates': templates
    }
    return render(request, 'main/school.html', data)

@login_required
@role_required(['director', 'admin'])
def school_edit(request):
    school = request.user.school
    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            return redirect('school')
    else:
        form = SchoolForm(instance=school)
    return render(request, 'main/school_edit.html', {'form': form})
# --- Optional AI handlers (оставляем как у тебя было) --- #
def ai(request):
    ans, q = '', ''
    if request.method == 'POST':
        file_contents = []

        if request.FILES.get('files'):
            for uploaded_file in request.FILES.getlist('files'):
                # Проверка формата
                if not uploaded_file.name.endswith('.docx'):
                    ans = "Файлҳо бояд формати docx дошта бошанд."
                    data = {'ans': ans, 'q': ''}
                    return render(request, 'main/AI.html', data)

                # Читаем напрямую из памяти (без сохранения на диск)
                file_contents.append(read_docx_with_tables(uploaded_file))

        # Директор
        director = User.objects.filter(school=request.user.school, role='director').first()
        director_info = f"имя директора школы {director.last_name} {director.first_name}"

        q = request.POST.get('query', '')
        if file_contents:
            merged_content = "----начало нового файла----".join(file_contents)
            # Формируем структурирующий промт
            ai_prompt = f"""Ты — ИИ для подготовки документов SmartDoc, готовых к печати в DOCX. 
Твоя задача — преобразовать любой текст документа в структурированный формат, используя маркеры:

1. [H] — заголовки и жирные фразы (например, названия документов, должности, фамилии руководителей)
2. [P] — обычный текст абзацев
3. [OL] — нумерованные списки
4. [UL] — маркированные списки

Особенности:
- Если в документе есть жирный заголовок (например, "ТАСДИҚНОМА"), помести его после [H]. 
- Если в строке есть обычный текст, после заголовка, помести его после [P] в новой строке.
- Не используйте специальные символы — разметка должна быть только с помощью [H], [P], [OL], [UL].
- Сохраняй смысл текста, не добавляй лишние пояснения.

Пример преобразования:

Исходный текст:
ТАСДИҚНОМА 
Дода шуд ба Шарипов Сӯҳробҷон Холбоевич...

Директори муассиса: Ахмедов Х.А.

Результат ИИ:
[H] ТАСДИҚНОМА
[P] Дода шуд ба Шарипов Сӯҳробҷон Холбоевич...
[H] Директори муассиса: Ахмедов Х.А.

Теперь запрос пользователя:

"{merged_content}"
и информация дополнительная информацыя{director_info}
        """
            ans = chatgpt(q + ai_prompt)
        else:ans = chatgpt(q + director_info)

    data = {'ans': ans, 'q': q}
    return render(request, 'main/AI.html', data)


@login_required
def save_docx(request):
    text = request.POST['text'].replace('<br>', '\n').replace(' ', ' ')
    title = request.POST.get('title', 'Барнома')
    type_id = request.POST.get('type', 1)

    doc = Document.objects.create(
        title=title,
        content=text,
        status='pending',
        category=Category.objects.get(pk=type_id),
        created_by=request.user,
        school=request.user.school,
    )
    ss=generate_final_doc(doc)  # сразу собираем с бланком
    print(ss.file)

    return redirect('index')
@login_required
def export_book(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Запись в книге учёта')
        add_export_book(title, request.user.school)
        return redirect('export_book')
    school=request.user.school
    export_book=ExportBook.objects.filter(school=school)
    return render(request,'main/export_book.html',{'ebook':export_book})
@login_required
def export_book_pdf(request):
    school = request.user.school
    entries = ExportBook.objects.filter(school=school).order_by('number')
    # === Настраиваем PDF ===
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="export_book_{school.name}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=40, bottomMargin=30)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Cyrillic', fontName='DejaVu', fontSize=11, leading=14))

    elements = []

    # === Заголовок ===
    title = Paragraph(f"<b>Экспортная книга школы:</b> {school.name}", styles['Cyrillic'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # === Таблица ===
    data = [["№", "Краткое описание", "Дата"]]

    for entry in entries:
        data.append([
            f"{entry.number:02d}",
            Paragraph(entry.title, styles['Cyrillic']),
            entry.created_at.strftime("%d.%m.%Y"),
        ])

    table = Table(data, colWidths=[40, 360, 100])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    elements.append(table)
    doc.build(elements)
    return response