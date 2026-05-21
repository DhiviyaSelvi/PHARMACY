import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

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
    query = request.GET.get('q')

    medicines = Medicine.objects.all()

    if category_id:
        medicines = medicines.filter(category_id=category_id)

    if query:
        medicines = medicines.filter(
            models.Q(name__icontains=query) |
            models.Q(company__icontains=query) |
            models.Q(description__icontains=query)
        )

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


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the signature
            client.utility.verify_payment_signature(params_dict)

            # Update order
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.status = 'COMPLETED'
            order.save()

            # Clear cart
            cart = Cart.objects.get(user=order.user)
            CartItem.objects.filter(cart=cart).delete()

            messages.success(request, "Payment successful! Your order has been placed.")
            return render(request, 'order_success.html')

        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('cart')
    return redirect('home')


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
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})


@login_required(login_url='/login/')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'order_detail.html', {'order': order, 'items': items})


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


def about_view(request):
    return render(request, 'about.html')


def contact_view(request):
    return render(request, 'contact.html')


@login_required(login_url='/login/')
def checkout(request):

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    total = sum(item.subtotal() for item in items)

    if request.method == 'POST':

        form = CheckoutForm(request.POST, request.FILES)

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

                    if order.payment_method == 'RAZORPAY':
                        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
                        payment = client.order.create({
                            'amount': int(total * 100),  # Amount in paise
                            'currency': 'INR',
                            'payment_capture': '1'
                        })
                        order.razorpay_order_id = payment['id']
                        order.save()

                        return render(request, 'checkout.html', {
                            'form': form,
                            'items': items,
                            'total': total,
                            'razorpay_order_id': payment['id'],
                            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
                            'razorpay_amount': payment['amount'],
                            'order_id': order.id,
                            'callback_url': request.build_absolute_uri('/payment/callback/')
                        })

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