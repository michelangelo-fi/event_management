event management system
michelangelo corsari
Django
E' una semplice applicazione in cui degli utenti organizer possono creare degli eventi, mentre altri utenti attendee vi si possono iscrivere.

Funzionalità implementate:
Attendee:
Registrazione e annullamento della registrazione a un evento
Consultazione dello storico delle proprie registrazioni ("I miei eventi")
Registrazione di un nuovo account e login/logout

Organizer:
Visualizzazione eventi
Creazione di nuovi eventi
Modifica ed eliminazione dei propri eventi (non di eventi altrui)
Visualizzazione della lista partecipanti per i propri eventi

Generali:
Visualizzazione della lista eventi (homepage pubblica)
Visualizzazione del dettaglio di un evento 
Autenticazione (login, logout, registrazione)
Permessi differenziati per ruolo, applicati sia lato interfaccia sia lato view
Feedback visivo (messaggi di successo/errore) per ogni azione
Pannello di amministrazione Django per la gestione avanzata dei dati

Il repository include il file db.sqlite3, già popolato

per installazione locale:
git clone (url)
cd event_management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
Visita http://127.0.0.1:8000

il database è db.sqlite3 ed è già stato popolato manualmente da me durante lo sviluppo e il testing

le consiglio di usare questi:
organizer password: multimediale
attendee  password: multimediale

superuser
giornogiovanna , password: multimediale

ovviamente in un vero progetto non dovrei committare un file con superuser e password

(altro superuser)
miche 
12345

http://127.0.0.1:8000/admin/ per andare all'admin panel (usare un superuser)

