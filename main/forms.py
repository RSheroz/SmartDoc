from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserRegistrationForm(UserCreationForm):
    role = ChoiceField(choices=User.ROLE_CHOICES)
    school = ModelChoiceField(queryset=School.objects.all())

    class Meta:
        model = User
        fields = ('username','first_name','last_name', 'email','avatar', 'role', 'school', 'password1', 'password2')
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'email': EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'password1': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
            'password2': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}),
        }

class TemplateForm(ModelForm):
    class Meta:
        model = Template
        fields = ['title', 'content']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter template title'}),
            'content': Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter template content'}),
        }


class DocumentForm(ModelForm):
    class Meta:
        model=Document
        fields=['title','content','category','status','file']
        widgets={
            'title':TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя документа'}),
            'content':Textarea(attrs={'class': 'form-control', 'placeholder': 'Содержание'}),
            'category':Select(attrs={'class': 'form-control ', 'placeholder': 'Тип документа','style':'max-width:max-content;'}),
            'status':Select(attrs={'class': 'form-control ', 'placeholder': 'Статус','style':'max-width:max-content;'}),
            'file':FileInput(attrs={'class': 'form-control', 'placeholder': 'Загрузить файл'}),
        }

class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'school']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'email': EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'role': Select(attrs={'class': 'form-control'}),
            'school': Select(attrs={'class': 'form-control'}),
        }