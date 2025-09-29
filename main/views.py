from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,logout as llogout
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q,Count
from django.http import JsonResponse
from .forms import *
from .gemini import *
from .models import *
import os,uuid,re,docx,datetime

def is_director_or_sec():
    pass

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'main/register.html'
    success_url = reverse_lazy('user_list')
    def get_queryset(self):
        # Только пользователи из своей школы
        return User.objects.filter(school=self.request.user.school)
class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'main/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def get_queryset(self):
        # Только пользователи из своей школы
        return User.objects.filter(school=self.request.user.school)
class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'main/document_form.html'
    success_url = reverse_lazy('documents')
class DocumentDeleteView(DeleteView):
    model = Document
    template_name = 'main/document_delete.html'
    success_url = '/'

class TemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'main/template_form.html'
    success_url = reverse_lazy('templates')

    def get_queryset(self):
        # Только шаблоны из своей школы
        return Template.objects.filter(school=self.request.user.school)
class TemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = Template
    template_name = 'main/template_confirm_delete.html'
    success_url = reverse_lazy('templates')

    def get_queryset(self):
        return Template.objects.filter(school=self.request.user.school)
    
@login_required
def index(request):
    docs=Document.objects.all().filter(school=request.user.school)
    templates=Template.objects.all().filter(school=request.user.school)
    stat=docs.aggregate(pending=Count('id',filter=Q(status='pending')),signed=Count('id',filter=Q(status='signed')))
    data={
        'docs':docs,
        'templates':templates,
        'stat':stat,
        'last_three_docs':docs.order_by('-created_at')[:3]
    }
    return render(request, 'main/index.html',data)

@login_required
def user_list(request):
    users = User.objects.filter(school=request.user.school)
    return render(request, 'main/user_list.html', {'users': users})
@login_required
def schools(request):
    schools = School.objects.annotate(
        user_count=models.Count('user', distinct=True),
        documents_count=models.Count('document',distinct=1)
    )
    return render(request, 'main/schools.html', {'schools': schools})
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
    templates=Template.objects.all().filter(school=request.user.school)
    return render(request,'main/templates.html', {"templates": templates})
@login_required
def template_create(request):
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.school = request.user.school
            template.save()
            return redirect('templates')
    else:
        form = TemplateForm()
    return render(request, 'main/template_form.html', {'form': form})
@login_required
def documents(request):
    documents=Document.objects.filter(school=request.user.school)
    templates=Template.objects.filter(school=request.user.school)
    users=User.objects.filter(school=request.user.school)
    data={'documents':documents,'templates':templates,'users':users}
    return render(request, 'main/documents.html', data)
@login_required
def fill_template(request,id):
    data = {}
    template_text=Template.objects.get(id=id)
    data['title']=template_text.title+f'{datetime.datetime.now().strftime(" %d.%m.%Y")}'
    template_text=template_text.content
    if request.method=='POST':
        form=DocumentForm(request.POST)
        res=template_text
        for k,v in request.POST.items():
            if k!='scrfmidlewaretoken':
                res=re.sub(r'\{\{\s*'+re.escape(k)+r'\s*\}\}',v,res)
        data['res']=res
        data['form']=form
    else:
        def replace_var(match):
            var_name=match.group(1)
            return f'<input type="text" class="fill" name="{var_name}" placeholder="{var_name}">'
        rendered_text=re.sub(r'\{\{\s*([\wа-яА-яёЁ\-]+)\s*\}\}',replace_var,template_text)
        data['data']=rendered_text
    return render(request, 'main/fill_template.html', data)
@login_required
def document_create(request):
    if request.method=='POST':
        form=DocumentForm(request.POST,request.FILES)
        if form.is_valid():
            doc=form.save(commit=False)
            doc.created_by = request.user
            doc.school = request.user.school
            doc.save()
            return redirect('documents')
        else:
            print(form.errors)
    else:
        form=DocumentForm(request.POST,request.FILES)
    return render(request, 'main\document_form.html',{'form':form})


def ai(request):
    ans,q='',''
    if request.method=='POST':
        if request.FILES.get('files'):
            path_list = []
            for i in request.FILES.getlist('files'):
                file_name = str(uuid.uuid4()) + '.' + i.name.split('.')[-1]
                save_path = os.path.join(settings.MEDIA_ROOT+"/documents/", file_name)
                with open(save_path, 'wb+') as destination:
                    for chunk in i.chunks():
                        destination.write(chunk)
                path_list+=[save_path]
        director = User.objects.filter(school=request.user.school, role='director').first()
        director=f'(есди нужно имя директора школы {director.last_name} {director.first_name} ответ не стилизовать(**, #))'
        q=request.POST['query']
        print(q)
        if request.FILES.get('files'):
            ans=send_file(path_list,q+director)
        else:
            ans=chatgpt(q+director)
    data={'ans':ans,'q':q}
    return render(request, 'main/AI.html',data)

def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    data = {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "status": document.status,
        "category": document.category.name,
        "status_display": document.get_status_display(),
        "created_by_name": document.created_by.username if document.created_by else None,
        "file":document.file.url,
        "created_at": document.created_at,
    }
    return JsonResponse(data, safe=False)

def save_docx(request):       
    text = request.POST['text'].replace('<br>', '\n').replace(' ', ' ')
    title = request.POST.get('title', 'Барнома')
    # add_export_book(f'Файли {title} дохил карда шуд')
    type_id = request.POST.get('type', 1)

    document = docx.Document()
    document.add_paragraph(text)

    file_name = str(uuid.uuid4()) + '.docx'
    path = os.path.join(settings.MEDIA_ROOT, "documents", file_name)
    document.save(path)

    # Создаём объект документа напрямую
    doc = Document.objects.create(
        title=title,
        status='pending',
        category=Category.objects.get(pk=type_id),
        created_by = request.user,
        school = request.user.school,
        file=f'documents/{file_name}'  # путь внутри MEDIA
    )
    return redirect('index')