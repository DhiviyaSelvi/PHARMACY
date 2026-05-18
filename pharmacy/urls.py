from django.urls import path

from . import views


urlpatterns = [

    path('', views.home, name='home'),

    path('cart/', views.cart_view, name='cart'),

    path(
        'add-to-cart/<int:medicine_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'increase/<int:item_id>/',
        views.increase_quantity,
        name='increase_quantity'
    ),

    path(
        'decrease/<int:item_id>/',
        views.decrease_quantity,
        name='decrease_quantity'
    ),

    path(
        'remove/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'signup/',
        views.signup_view,
        name='signup'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

]