from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import login, logout
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView
from django.views.generic.detail import DetailView
from cursos.forms import RegistroUsuarioForm, CursoForm
from cursos.models import Curso

# Create your views here.

class ListaCursosView(LoginRequiredMixin, ListView):
    model = Curso
    template_name = 'cursos/lista_cursos.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        if self.request.user.rol == 'admin':
            return Curso.objects.all()
        return Curso.objects.filter(estado=True)
    
class DetalleCursoView(LoginRequiredMixin, DetailView):
    model = Curso
    template_name = 'cursos/detalle_curso.html'
    context_object_name = 'curso'

class InscribirCursoView(LoginRequiredMixin, DetailView):
    model = Curso

    def get(self, request, *args, **kwargs):
        curso = self.get_object()
        if request.user not in curso.inscritos.all() and curso.inscritos.count() < curso.cupos:
            curso.inscritos.add(request.user)
            messages.success(request, f'Inscripción exitosa en el curso {curso.nombre}')
        else:
            messages.error(request, f'No se pudo realizar la inscripcion en el curso {curso.nombre}')
        return redirect('detalle_curso', pk=curso.pk)

class MisCursosView(LoginRequiredMixin,  ListView):
    model = Curso
    template_name = 'cursos/lista_cursos.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        return self.request.user.cursos_inscritos.all()

class CrearCursoView(LoginRequiredMixin, UserPassesTestMixin,  CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'cursos/curso_form.html'
    success_url = reverse_lazy('lista_cursos')

    def test_func(self):
        return self.request.user.rol == 'admin'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'El curso se ha creado correctamente')
        return response


class CustomLoginView(LoginView):
    template_name = 'registro/login.html'

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos. Por favor, ingrese nuevamene.')
        return super().form_invalid(form)
    
class CustomLogoutView(View):
    
    def get(self, request):
        logout(request)
        messages.success(request, 'Sesion cerrada correctamente.')
        response = redirect('login')
        response['Cache-Control'] = 'no-cache', 'no-store', 'must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

class RegistroUsuarioView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'registro/registro.html'
    success_url = reverse_lazy('lista_cursos')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Se ha registrado exitosamente. ")
        return response
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
            return super().form_invalid(form)