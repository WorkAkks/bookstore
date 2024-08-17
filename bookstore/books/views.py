from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Book, Category, Order, OrderItem
from .forms import BookForm, OrderForm, UserRegistrationForm, UserLoginForm


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


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order_item = form.save(commit=False)
            order_item.book = book
            order_item.order = Order.objects.create(user=request.user)
            order_item.save()
            return redirect('cart')
    else:
        form = OrderForm()
    return render(request, 'books/add_to_cart.html', {'form': form, 'book': book})


def cart(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
        order_items = OrderItem.objects.filter(order=order)
        total_price = sum([item.book.price * item.quantity for item in order_items])
        return render(request, 'books/cart.html', {'order_items': order_items, 'total_price': total_price})
    else:
        return redirect('login')


@login_required
def checkout(request):
    if request.method == 'POST':
        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
        order.is_completed = True
        order.save()
        return redirect('book_list')
    return render(request, 'books/checkout.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'books/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
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
        form = UserLoginForm()
    return render(request, 'books/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('book_list')