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

    #Личный кабинет и корзина
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='orders'),
    path('check_username/', views.check_username, name='check_username'),
]
