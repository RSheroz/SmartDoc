from django.contrib.auth.models import AbstractUser
from django.db import models

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    tel=models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} - {self.address}'


class User(AbstractUser):
    ROLE_CHOICES = (
        ('director', 'Директор'),
        ('secretary', 'Секретарь'),
        ('teacher', 'Учитель'),
    )
    avatar=models.ImageField(upload_to='avatars/' ,default='avatars/default.png')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
class Template(models.Model):
    title = models.CharField(max_length=255)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    content = models.TextField(help_text="Используй переменные: {{ ФИО }}, {{ дата }}, и т.д.")
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Document(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('pending', 'На проверке'),
        ('signed', 'Подписан'),
        ('rejected','Отклонен')
    )

    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents_created')
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents_received')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    file=models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
