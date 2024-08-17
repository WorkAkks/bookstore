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


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)