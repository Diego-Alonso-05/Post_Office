# PostOffice_App/views/decorators.py
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def role_required(allowed_roles):
    """
    Decorator to restrict access by request.user.role.
    allowed_roles: list like ["admin", "manager", "client"]
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("login")  # o tu ruta de login

            role = getattr(user, "role", None)
            if role not in allowed_roles:
                return HttpResponseForbidden("No tienes permisos para ver esto.")

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
