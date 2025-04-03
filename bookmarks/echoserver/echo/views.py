import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.contrib import messages
from .models import Book
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
                return redirect('book_list')
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
    context = {
        'books': books,
        'is_authenticated': 'user_id' in request.session,
        'username': request.session.get('username'),
        'is_admin': request.session.get('role') == 'admin'
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
