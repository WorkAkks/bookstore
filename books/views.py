from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from .models import Book, Order, OrderItem, Category
from .forms import BookForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.contrib import messages


def book_list(request):
    books = Book.objects.all()
    categories = Category.objects.all()
    author = request.GET.get('author')
    category = request.GET.get('category')
    year = request.GET.get('year')
    if author:
        books = books.filter(author__icontains=author)
    if category:
        books = books.filter(category__name=category)
    if year:
        books = books.filter(publication_year=year)
    return render(request, 'books/book_list.html', {'books': books, 'categories': categories})


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_detail.html', {'book': book})


def cart(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
        order_items = OrderItem.objects.filter(order=order)
        if request.method == 'POST':
            for item in order_items:
                rental_period = request.POST.get(f'rental_period_{item.id}')
                if rental_period:
                    item.rental_period = rental_period
                    item.is_rent = rental_period != 'покупка'
                    item.save()
            return redirect('cart')
        total_price = 0
        total_purchase = 0
        total_rental = 0
        item_details = []
        for item in order_items:
            for _ in range(item.quantity):
                if item.is_rent:
                    if item.rental_period == '2 недели':
                        rental_price = item.book.price / 20
                    elif item.rental_period == 'месяц':
                        rental_price = item.book.price / 10
                    elif item.rental_period == '3 месяца':
                        rental_price = item.book.price / 5
                    item_total = rental_price
                    item_type = 'аренда'
                    total_rental += item_total
                else:
                    item_total = item.book.price
                    item_type = 'покупка'
                    total_purchase += item_total
                total_price += item_total
                item_details.append({
                    'title': item.book.title,
                    'item_total': item_total,
                    'item_type': item_type,
                    'rental_period': item.rental_period,
                    'order_item_id': item.id,
                })
        return render(request, 'books/cart.html', {
            'item_details': item_details,
            'total_price': total_price,
            'total_purchase': total_purchase,
            'total_rental': total_rental,
        })
    else:
        return redirect('login')


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
    order_item, created = OrderItem.objects.get_or_create(
        book=book,
        order=order,
        defaults={'quantity': 0}
    )
    if request.method == 'POST':
        order_item.quantity += 1
        order_item.save()
        return JsonResponse({'quantity': order_item.quantity, 'book_id': book.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def remove_from_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    order = Order.objects.get(user=request.user, is_completed=False)
    order_item = OrderItem.objects.filter(book=book, order=order).first()
    if order_item and order_item.quantity > 0:
        order_item.quantity -= 1
        if order_item.quantity == 0:
            order_item.delete()
        else:
            order_item.save()
        return JsonResponse({'quantity': order_item.quantity})
    return JsonResponse({'quantity': 0})


def checkout(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)

        # Проверяем, есть ли у нас элементы в корзине
        if order.orderitem_set.exists():
            # Удаляем все элементы из корзины
            order_items = OrderItem.objects.filter(order=order)
            order_items.delete()

            # Отправляем сообщение об успешном заказе
            messages.success(request, 'Заказ оформлен! Ваша корзина очищена.')
        else:
            # Если корзина пуста
            messages.warning(request, 'Ваша корзина пуста.')

        # Перенаправляем к главной странице книг
        return redirect('book_list')

    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = UserCreationForm()
    return render(request, 'books/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book_list')
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'books/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('book_list')

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def manage_books(request):
    books = Book.objects.all()
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_books')
    else:
        form = BookForm()

    return render(request, 'books/manage_books.html', {'books': books, 'form': form})

@login_required
@user_passes_test(is_admin)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('manage_books')
    else:
        form = BookForm(instance=book)

    return render(request, 'books/edit_book.html', {'form': form, 'book': book})


def update_order_item(request, item_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, id=item_id)
        quantity = request.POST.get('quantity')
        order_item.quantity = quantity
        rental_option = request.POST.get('rental_option')
        if rental_option == 'purchase':
            order_item.is_rent = False
            order_item.rental_period = None
        elif rental_option == 'rental_2_weeks':
            order_item.is_rent = True
            order_item.rental_period = '2 недели'
        elif rental_option == 'rental_month':
            order_item.is_rent = True
            order_item.rental_period = 'месяц'
        elif rental_option == 'rental_3_months':
            order_item.is_rent = True
            order_item.rental_period = '3 месяца'
        order_item.save()
        return redirect('cart')