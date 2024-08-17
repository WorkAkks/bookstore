from django import forms
from .models import Book, Order, OrderItem, User


class OrderItemForm(forms.ModelForm):
    RENTAL_PERIOD_CHOICES = [
        ('покупка', 'Покупка'),
        ('2 недели', 'Аренда на 2 недели'),
        ('месяц', 'Аренда на месяц'),
        ('3 месяца', 'Аренда на 3 месяца'),
    ]
    rental_period = forms.ChoiceField(choices=RENTAL_PERIOD_CHOICES, required=True)
    class Meta:
        model = OrderItem
        fields = ['quantity', 'rental_period']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'price', 'status']