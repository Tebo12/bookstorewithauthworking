from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if request.session.get('role') != 'admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('book_list')
        return view_func(request, *args, **kwargs)
    return wrapper