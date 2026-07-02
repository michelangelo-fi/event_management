from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from .models import Event, Registration


def event_list(request):
    """Homepage: mostra tutti gli eventi ordinati per data, visibile a chiunque."""
    events = Event.objects.all().order_by('date')
    return render(request, 'events/event_list.html', {'events': events})


class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    #Creazione evento, riservata agli Organizer (vedi test_func)
    model = Event
    fields = ['title', 'description', 'date', 'location', 'max_attendees']
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        # UserPassesTestMixin chiama questo metodo prima di mostrare la view:
        # se restituisce False, Django blocca l'accesso con un 403
        return self.request.user.is_organizer()

    def get_form(self, form_class=None):
        # Forza il campo data a usare il selettore nativo HTML5 (datetime-local)
        # invece del formato testuale di default, che risulterebbe in formato
        # americano mese/giorno/anno.
        form = super().get_form(form_class)
        form.fields['date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        form.fields['date'].input_formats = ['%Y-%m-%dT%H:%M']
        return form

    def form_valid(self, form):
        # L'organizer non è un campo del form (l'utente non lo sceglie):
        # viene impostato automaticamente sull'utente loggato prima del salvataggio.
        form.instance.organizer = self.request.user
        return super().form_valid(form)


class EventDetailView(DetailView):
    #Pagina di dettaglio evento, pubblica (nessun mixin di permessi)
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        # Aggiunge al contesto un flag che dice al template se l'utente
        # loggato è già registrato a questo evento, per decidere se
        # mostrare il bottone "Registrati" o "Annulla registrazione".
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_is_registered'] = Registration.objects.filter(
                event=self.object, attendee=self.request.user
            ).exists()
        return context


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    #solo l'Organizer proprietario dell'evento può accedere
    model = Event
    fields = ['title', 'description', 'date', 'location', 'max_attendees']
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        # Doppio controllo: ruolo Organizer E proprietà dell'evento specifico,
        # altrimenti un Organizer potrebbe modificare eventi altrui.
        event = self.get_object()
        return self.request.user.is_organizer() and event.organizer == self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        form.fields['date'].input_formats = ['%Y-%m-%dT%H:%M']
        return form


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    #Eliminazione evento: stesso controllo di proprietà di EventUpdateView
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        event = self.get_object()
        return self.request.user.is_organizer() and event.organizer == self.request.user


@login_required
def event_register(request, pk):
    """
    Registrazione di un Attendee a un evento.
    Funzione (non class based view) perché la logica ha più condizioni di business
    concatenate (ruolo, doppia registrazione, posti disponibili) che
    risultano più chiare in una vista esplicita
    """
    event = get_object_or_404(Event, pk=pk)

    # Solo gli Attendee possono registrarsi (un Organizer non si iscrive agli eventi)
    if not request.user.is_attendee():
        messages.error(request, 'Solo gli Attendee possono registrarsi agli eventi.')
        return redirect('event_detail', pk=pk)

    # Evita registrazioni duplicate dello stesso utente allo stesso evento
    # (c'è anche un vincolo unique_together nel modello come sicurezza a livello DB)
    if Registration.objects.filter(event=event, attendee=request.user).exists():
        messages.warning(request, 'Sei già registrato a questo evento.')
        return redirect('event_detail', pk=pk)

    # Controllo posti disponibili: conta le registrazioni esistenti e le
    # confronta col limite dell'evento. Nessun controllo "and" superfluo:
    # funziona correttamente anche quando max_attendees è 0.
    current_registrations = Registration.objects.filter(event=event).count()
    if current_registrations >= event.max_attendees:
        messages.error(request, 'Posti esauriti per questo evento.')
        return redirect('event_detail', pk=pk)

    Registration.objects.create(event=event, attendee=request.user)
    messages.success(request, 'Registrazione avvenuta con successo!')
    return redirect('event_detail', pk=pk)


@login_required
def event_unregister(request, pk):
    #Annulla la registrazione dell'utente loggato a un evento
    event = get_object_or_404(Event, pk=pk)
    registration = Registration.objects.filter(event=event, attendee=request.user).first()

    if registration:
        registration.delete()
        messages.success(request, 'Registrazione annullata.')
    else:
        messages.warning(request, 'Non risulti registrato a questo evento.')

    return redirect('event_detail', pk=pk)


class EventAttendeesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    #Lista dei partecipanti a un evento, visibile solo all'Organizer proprietario
    model = Registration
    template_name = 'events/event_attendees.html'
    context_object_name = 'registrations'

    def test_func(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        return self.request.user.is_organizer() and event.organizer == self.request.user

    def get_queryset(self):
        self.event = get_object_or_404(Event, pk=self.kwargs['pk'])
        # select_related evita una query separata per ogni "attendee" nel
        # loop del template: recupera evento e utente in un'unica join.
        return Registration.objects.filter(event=self.event).select_related('attendee')

    def get_context_data(self, **kwargs):
        # self.event viene calcolato dentro get_queryset, che Django chiama
        # sempre prima di get_context_data — quindi qui è già disponibile.
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context


class MyRegistrationsView(LoginRequiredMixin, ListView):
    #Storico eventi a cui l'utente loggato si è registrato ('I miei eventi')
    model = Registration
    template_name = 'events/my_registrations.html'
    context_object_name = 'registrations'

    def get_queryset(self):
        return Registration.objects.filter(
            attendee=self.request.user
        ).select_related('event').order_by('event__date')