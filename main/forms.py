from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from .models import *


class SchoolRegistrationForm(Form):
    # ====== Данные школы ======
    school_name = CharField(label="Название школы", max_length=255)
    address = CharField(label="Адрес", max_length=255, required=False)
    email = EmailField(label="Email", required=False)
    tel = CharField(label="Телефон", max_length=20, required=False)
    headletter = FileField(label="Шапка школы (HeadLetter)", required=False)

    # ====== Данные директора ======
    username = CharField(label="Логин директора", max_length=150)
    first_name = CharField(label="Имя директора", max_length=150)
    last_name = CharField(label="Фамилия директора", max_length=150)
    password = CharField(label="Пароль", widget=PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Логин уже занят. Пожалуйста, выберите другой.")
        return username

    def save(self):
        # Создание школы
        school = School.objects.create(
            name=self.cleaned_data['school_name'],
            address=self.cleaned_data['address'],
            email=self.cleaned_data['email'],
            tel=self.cleaned_data['tel'],
            headletter=self.cleaned_data.get('headletter')
        )

        # Создание пользователя-директора
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='director',
            is_active=False  # Директор не активен до подтверждения
        )

        # Можно добавить связь между директором и школой, если есть ForeignKey
        user.school = school
        user.save()

        return school

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