from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Excluir la ruta de administración
        admin_path = reverse('admin:index')
        
        if not request.user.is_authenticated and not request.path.startswith(reverse('login')) and not request.path.startswith(admin_path):
            return redirect('login')
        
        
""" class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path.startswith(reverse('login')):
            return redirect('login')
        return self.get_response(request) """