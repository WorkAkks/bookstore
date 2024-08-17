from django import forms
from .models import Book, Order, OrderItem, User


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'


class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity']
