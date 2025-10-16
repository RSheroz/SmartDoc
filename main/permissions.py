from django.core.exceptions import PermissionDenied
from functools import wraps
from django.http import HttpResponse

def role_required(allowed_roles):
    """
    Проверяет, что у пользователя есть одна из разрешённых ролей.
    Пример:
    @role_required(['director', 'secretary'])
    def my_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponse("❌ Доступ запрещён. Войдите в систему.", status=403)

            if request.user.role not in allowed_roles:
                return HttpResponse("❌ У вас нет прав для доступа к этой странице.", status=403)


            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = []

    def handle_no_permission(self):
        return HttpResponse("❌ У вас нет прав для доступа к этой странице.", status=403)
    def test_func(self):
        return self.request.user.role in self.allowed_roles


class DirectorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['director']


class SecretaryRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['secretary']


class TeacherRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['teacher']


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']
