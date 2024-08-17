from bookstore.celery import app
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import Rental

@app.task
def send_rental_reminders():
    now = timezone.now()
    soon_expiring_rentals = Rental.objects.filter(rental_end__lt=now + timezone.timedelta(days=3))
    for rental in soon_expiring_rentals:
        send_mail(
            'Напоминание об окончании аренды',
            f"Уважаемый(ая) {rental.user.username}, напоминаем, что срок аренды книги '{rental.book.title}' истекает через 3 дня.",
            'from@example.com',
            [rental.user.email],
            fail_silently=False,
        )