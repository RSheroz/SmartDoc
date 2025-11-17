from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', index, name='index'),  # Главная страница после входа
    path('add_user/', add_user, name='register'),
    path('export_book',export_book,name='export_book'),
    path('export_book/pdf/', export_book_pdf, name='export_book_pdf'),
    path('standard_docs/', standard_docs, name='standard_docs'),
    path('login/', login_view,name='login'), #auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', logout, name='logout'),
    path('user_list/', user_list, name='user_list'),
    path('user_edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('user_delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('profile/', profile, name='profile'),
    path('school/', school, name='school'),
    path('school_edit/', school_edit, name='school_edit'),
    path('school_reg/', school_reg, name='school_reg'),
    path('ai',ai,name='ai'),
    path('templates/',templates, name='templates'),
    path('template_create/',template_create, name='template_create'),
    path('templates/edit-<int:pk>', TemplateUpdateView.as_view(), name='edit_template'),
    path('templates/dalete-<int:pk>', TemplateDeleteView.as_view(), name='delete_template'),
    path('fill-<int:id>',fill_template,name='fill_template'),
    path('documents/', documents, name='documents'),
    path('document_create/',document_create,name='document_create'),
    path('documents/edit-<int:pk>/', DocumentUpdateView.as_view(), name='document_edit'),
    path('documents/delete-<int:pk>/', DocumentDeleteView.as_view(), name='document_delete'),
    path('api/documents/<int:pk>/', document_detail, name='api_document_detail'),
    path('save_docx',save_docx,name='save_docx'),
]