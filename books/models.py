from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image = models.ImageField(upload_to='images/')
    status = models.CharField(max_length=20, choices=[
        ('available', 'Доступна'),
        ('out_of_stock', 'Недоступна'),
    ])

    def __str__(self):
        return self.title


User = get_user_model()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_rent = models.BooleanField(default=False)
    rental_period = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.book.title} - {self.quantity}"

class Rental(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rental_start = models.DateTimeField(auto_now_add=True)
    rental_end = models.DateTimeField()
    rental_type = models.CharField(max_length=20, choices=[('2 недели', '2 недели'), ('месяц', 'месяц'), ('3 месяца', '3 месяца')])

    def __str__(self):
        return f"{self.user} rented {self.book}"

