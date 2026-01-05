from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from main.models import School, User, Document
from smartadmin.forms import *

def is_superadmin(user):
    return user.is_superuser or getattr(user, 'role', '') == 'director'


@login_required
@user_passes_test(is_superadmin)
def dashboard(request):
    context = {
        'school_count': School.objects.count(),
        'approved_schools': School.objects.filter(approved=True).count(),
        'pending_schools': School.objects.filter(approved=False).count(),
        'user_count': User.objects.count(),
        'doc_count': Document.objects.count(),
    }
    return render(request, 'smartadmin/dashboard.html', context)


@login_required
@user_passes_test(is_superadmin)
def schools(request):
    schools = School.objects.all().order_by('-created_at')
    return render(request, 'smartadmin/schools.html', {'schools': schools})


@login_required
@user_passes_test(is_superadmin)
def approve_school(request, school_id):
    school = get_object_or_404(School, id=school_id)
    school.approved = True
    school.save()
    # Активировать директора школы
    director = User.objects.filter(school=school, role='director').first()
    if director:
        director.is_active = True
        director.save()
    messages.success(request, f'Школа "{school.name}" одобрена.')
    return redirect('smartadmin:schools')


@login_required
@user_passes_test(is_superadmin)
def reject_school(request, school_id):
    school = get_object_or_404(School, id=school_id)
    school.approved = False
    school.save()
    messages.warning(request, f'Школа "{school.name}" отклонена.')
    return redirect('smartadmin:schools')


@login_required
@user_passes_test(is_superadmin)
def delete_school(request, school_id):
    school = get_object_or_404(School, id=school_id)
    school.delete()
    messages.error(request, f'Школа "{school.name}" удалена.')
    return redirect('smartadmin:schools')


@login_required
@user_passes_test(is_superadmin)
def users(request):
    users = User.objects.all().order_by('role')
    return render(request, 'smartadmin/users.html', {'users': users})


@login_required
@user_passes_test(is_superadmin)
def documents(request):
    documents = Document.objects.all().order_by('-created_at')
    return render(request, 'smartadmin/documents.html', {'documents': documents})


@login_required
@user_passes_test(is_superadmin)
def analytics(request):
    schools = School.objects.all()
    school_stats = []
    for s in schools:
        user_count = User.objects.filter(school=s).count()
        doc_count = Document.objects.filter(created_by__school=s).count()
        school_stats.append({
            'name': s.name,
            'approved': s.approved,
            'user_count': user_count,
            'doc_count': doc_count,
        })

    context = {
        'schools_count': schools.count(),
        'approved_schools': schools.filter(approved=True).count(),
        'users_count': User.objects.count(),
        'documents_count': Document.objects.count(),
        'school_stats': school_stats,
    }
    return render(request, 'smartadmin/analytics.html', context)


@login_required
@user_passes_test(is_superadmin)
def edit_school(request, school_id):
    school = get_object_or_404(School, id=school_id)
    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'Данные школы "{school.name}" успешно обновлены!')
            return redirect('smartadmin:schools')
        else:
            messages.error(request, 'Ошибка при сохранении формы.')
    else:
        form = SchoolForm(instance=school)
    return render(request, 'smartadmin/edit_school.html', {'form': form, 'school': school})