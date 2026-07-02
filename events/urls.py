from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('<int:pk>/register/', views.event_register, name='event_register'),
    path('<int:pk>/unregister/', views.event_unregister, name='event_unregister'),
    path('<int:pk>/attendees/', views.EventAttendeesView.as_view(), name='event_attendees'),
    path('my-registrations/', views.MyRegistrationsView.as_view(), name='my_registrations'),
]