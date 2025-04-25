import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.contrib import messages
from .models import Book, User, CartItem, Order, OrderItem
from .forms import RegistrationForm, LoginForm, BookForm
from .utils import login_required, admin_required

import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from .models import Book, User
from .forms import RegistrationForm, LoginForm, BookForm
from .utils import login_required, admin_required

from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.http import JsonResponse

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'],
                        email=form.cleaned_data['email'],
                        first_name=form.cleaned_data['first_name']
                    )
                    

                    print(f"Debug: User saved to database:")
                    print(f"- Username: {user.username}")
                    print(f"- Password hash: {user.password}")

                    verify_user = User.objects.get(id=user.id)
                    print(f"✅ Verified user exists in database: {verify_user.username}")
                    
                    messages.success(request, 'Регистрация успешна! Войдите в аккаунт.')
                    return redirect('login')
            except Exception as e:
                print(f"[REGISTER ERROR] {str(e)}", file=sys.stderr)
                messages.error(request, 'Ошибка регистрации. Попробуйте снова.')
        else:
            print(f"[REGISTER ERROR] Некорректная форма: {form.errors}", file=sys.stderr)
            messages.error(request, 'Некорректные данные.')

    return render(request, 'register.html', {'form': RegistrationForm()})


def login(request):
    print("login request:", request.method)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        print(f"🔍 Попытка входа: {username}", file=sys.stderr)

        print("All users in database:")
        all_users = User.objects.all()
        for u in all_users:
            print(f"- {u.username}")

        try:
            user = User.objects.get(username=username)
            print("Found user:", user.username)
            print("Stored hash:", user.password)
            print("Password check result:", check_password(password, user.password))
            
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['role'] = user.role
                request.session['username'] = user.username
                print(f"✅ Успешная аутентификация пользователя: {user.username}", file=sys.stderr)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                response = redirect('book_list')
                response.set_cookie('last_visited', datetime.now(), max_age=30*24*60*60)
                return response
            else:
                print(f"❌ Ошибка входа: Неверный пароль для {username}", file=sys.stderr)
                messages.error(request, 'Неверное имя пользователя или пароль.')
        except User.DoesNotExist:
            print(f"User not found: {username}")
            similar_users = User.objects.filter(username__icontains=username)
            if similar_users.exists():
                print("Found similar usernames:")
                for u in similar_users:
                    print(f"- {u.username}")
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'login.html', {'form': LoginForm()})


def logout(request):
    request.session.flush()
    messages.success(request, 'Вы вышли из системы.')
    return redirect('book_list')



def book_list(request):
    books = Book.objects.all()
    
    # Фильтрация
    if author := request.GET.get('author'):
        books = books.filter(author__icontains=author)
    if min_price := request.GET.get('min_price'):
        books = books.filter(price__gte=min_price)
    if max_price := request.GET.get('max_price'):
        books = books.filter(price__lte=max_price)
    
    context = {
        'books': books,
        'is_authenticated': 'user_id' in request.session,
        'username': request.session.get('username'),
        'is_admin': request.session.get('role') == 'admin',
        'cart_items_count': CartItem.objects.filter(
            user_id=request.session.get('user_id')
        ).count() if 'user_id' in request.session else 0
    }
    return render(request, 'book_list.html', context)


@login_required
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно добавлена!')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_add.html', {'form': form})


@admin_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно обновлена!')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_edit.html', {'form': form})


@admin_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга удалена.')
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})

@login_required
def profile(request):
    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.save()
        messages.success(request, 'Данные успешно обновлены!')
        return redirect('profile')
    return render(request, 'profile.html', {'user': user})

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user_id=request.session['user_id']).select_related('book')
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user_id = request.session['user_id']
    
    cart_item, created = CartItem.objects.get_or_create(
        user_id=user_id,
        book=book,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, 'Книга добавлена в корзину')
    return redirect('book_list')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, user_id=request.session['user_id'])
    cart_item.delete()
    messages.success(request, 'Книга удалена из корзины')
    return redirect('cart')

@login_required
def checkout(request):
    user_id = request.session['user_id']
    cart_items = CartItem.objects.filter(user_id=user_id).select_related('book')
    
    if not cart_items:
        messages.error(request, 'Корзина пуста')
        return redirect('cart')
    
    total = sum(item.book.price * item.quantity for item in cart_items)
    
    with transaction.atomic():
        order = Order.objects.create(
            user_id=user_id,
            total_price=total
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )
        
        cart_items.delete()
    
    messages.success(request, f'Заказ #{order.id} успешно оформлен!')
    return redirect('orders')

@login_required
def order_history(request):
    orders = Order.objects.filter(user_id=request.session['user_id']).prefetch_related('orderitem_set__book')
    return render(request, 'orders.html', {'orders': orders})

def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})
