from celery import Celery
from django.conf import settings

app = Celery('bookstore')

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()

@app.task
def send_rental_reminders():
    from datetime import timedelta
    from django.utils import timezone
    from django.core.mail import send_mail
    from books.models import Rental

    rentals = Rental.objects.filter(
        rental_end__lt=timezone.now() + timedelta(days=3),
        rental_end__gt=timezone.now()
    )
    for rental in rentals:
        send_mail(
            'Напоминание об окончании срока аренды',
            f"Уважаемый(ая) {rental.user.username}, напоминаем, что срок аренды книги '{rental.book.title}' истекает через 3 дня.",
            'your_email@example.com',
            [rental.user.email],
        )
