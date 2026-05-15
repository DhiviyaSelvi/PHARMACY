from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

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


@login_required
def add_to_cart(request, medicine_id):

    medicine = get_object_or_404(Medicine, id=medicine_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        medicine=medicine
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


@login_required
def cart_view(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    items = CartItem.objects.filter(cart=cart)

    total = 0

    for item in items:
        total += item.subtotal()

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


@login_required
def increase_quantity(request, item_id):

    item = CartItem.objects.get(id=item_id)

    item.quantity += 1

    item.save()

    return redirect('cart')


@login_required
def decrease_quantity(request, item_id):

    item = CartItem.objects.get(id=item_id)

    item.quantity -= 1

    if item.quantity <= 0:
        item.delete()
    else:
        item.save()

    return redirect('cart')


@login_required
def remove_item(request, item_id):

    item = CartItem.objects.get(id=item_id)

    item.delete()

    return redirect('cart')


@login_required
def checkout(request):

    cart = Cart.objects.get(user=request.user)

    items = CartItem.objects.filter(cart=cart)

    total = 0

    for item in items:
        total += item.subtotal()

    if request.method == 'POST':

        form = CheckoutForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)

            order.user = request.user

            order.total_amount = total

            order.save()

            for item in items:

                OrderItem.objects.create(
                    order=order,
                    medicine=item.medicine,
                    quantity=item.quantity,
                    price=item.medicine.price
                )

            items.delete()

            return render(request, 'order_success.html')

    else:

        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'items': items,
        'total': total
    })