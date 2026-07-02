from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
#from django.contrib.auth.decorators import login_required
from .forms import RegisterForm

#crea un nuovo account e lo autentica subito
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registrazione completata!')
            return redirect('event_list')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

#login dell'utente con autenticazione manuale, non uso loginview di django perché voglio gestire il messaggio di errore in caso di credenziali non valide
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('event_list')
        else:
            messages.error(request, 'Credenziali non valide.')
    return render(request, 'accounts/login.html')

#logout dell'utente, reindirizzandolo alla pagina di login
def logout_view(request):
    logout(request)
    return redirect('login')