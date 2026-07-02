from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ATTENDEE = 'attendee'
    ORGANIZER = 'organizer'

    ROLE_CHOICES = [
        (ATTENDEE, 'Attendee'),
        (ORGANIZER, 'Organizer'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ATTENDEE)

    def is_organizer(self):
        return self.role == self.ORGANIZER

    def is_attendee(self):
        return self.role == self.ATTENDEE