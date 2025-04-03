from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Книги
    path('', views.book_list, name='book_list'),
    path('add/', views.book_add, name='book_add'),
    path('edit/<int:pk>/', views.book_edit, name='book_edit'),
    path('delete/<int:pk>/', views.book_delete, name='book_delete'),

    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
