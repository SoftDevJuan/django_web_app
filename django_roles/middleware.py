from django.shortcuts import redirect
from django.urls import reverse

class GroupRedirectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.excluded_urls = [
            reverse('logout'),
        ]
        
        self.target_url = reverse('Autorizacion Pendiente')

    def __call__(self, request):
        if request.user.is_authenticated:
            group_name = 'Autorizacion-Pendiente'

            # Redirige a los usuarios del grupo específico a la vista específica
            if self.user_in_group(request.user, group_name):
                if request.path not in self.excluded_urls and request.path != self.target_url:
                    return redirect(self.target_url)
            # Redirige a los usuarios que no pertenecen al grupo específico al inicio
            elif request.path == self.target_url:
                return redirect(reverse('Inicio')) 

        response = self.get_response(request)
        return response

    def user_in_group(self, user, group_name):
        return user.groups.filter(name=group_name).exists()
