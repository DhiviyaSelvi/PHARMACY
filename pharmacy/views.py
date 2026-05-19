from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from .models import *
from .forms import CheckoutForm


def home(request):

    categories = Category.objects.all()

    category_id = request.GET.get('category')

    if category_id:

        medicines = Medicine.objects.filter(
            category_id=category_id
        )

    else:

        medicines = Medicine.objects.all()

    return render(request, 'home.html', {
        'medicines': medicines,
        'categories': categories
    })


@login_required(login_url='/login/')
def add_to_cart(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)

    if medicine.stock <= 0:
        messages.warning(request, f"Sorry, {medicine.name} is out of stock.")
        return redirect('home')

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        medicine=medicine
    )

    if not item_created:
        if cart_item.quantity < medicine.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added another {medicine.name} to your cart.")
        else:
            messages.warning(request, f"Sorry, only {medicine.stock} items in stock.")
    else:
        # Check stock for newly created cart item too
        if cart_item.quantity > medicine.stock:
            cart_item.delete()
            messages.warning(request, f"Sorry, {medicine.name} is out of stock.")
            return redirect('home')
        messages.success(request, f"{medicine.name} added to cart.")

    return redirect('cart')


@login_required(login_url='/login/')
def cart_view(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = CartItem.objects.filter(cart=cart)

    total = 0

    for item in items:
        total += item.subtotal()

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


@login_required(login_url='/login/')
def increase_quantity(request, item_id):

    item = CartItem.objects.get(id=item_id)

    if item.quantity < item.medicine.stock:

        item.quantity += 1
        item.save()

    return redirect('/cart/')


@login_required(login_url='/login/')
def decrease_quantity(request, item_id):

    item = CartItem.objects.get(id=item_id)

    if item.quantity > 1:

        item.quantity -= 1
        item.save()

    else:

        item.delete()

    return redirect('/cart/')


@login_required(login_url='/login/')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    medicine_name = item.medicine.name
    item.delete()
    messages.info(request, f"Removed {medicine_name} from cart.")
    return redirect('cart')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):

    logout(request)

    return redirect('/login/')


@login_required(login_url='/login/')
def checkout(request):

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    total = sum(item.subtotal() for item in items)

    if request.method == 'POST':

        form = CheckoutForm(request.POST)

        if form.is_valid():
            from django.db import transaction
            from django.db.models import F

            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_amount = total

                    # Set status based on payment method
                    if order.payment_method == 'CASH':
                        order.status = 'PROCESSING'
                    else:
                        order.status = 'PENDING'

                    order.save()

                    for item in items:
                        # Re-check stock atomically
                        medicine = Medicine.objects.select_for_update().get(id=item.medicine.id)
                        if medicine.stock < item.quantity:
                            raise ValueError(f"Not enough stock for {medicine.name}")

                        OrderItem.objects.create(
                            order=order,
                            medicine=medicine,
                            quantity=item.quantity,
                            price=medicine.price
                        )

                        medicine.stock = F('stock') - item.quantity
                        medicine.save()

                    items.delete()
                    messages.success(request, "Order placed successfully!")
                    return render(request, 'order_success.html')
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart')

    else:

        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'items': items,
        'total': total
    })